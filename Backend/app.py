from flask import Flask, request, jsonify
import requests, os, threading, uuid
import uvicorn
from fastapi_back import router
from typing import Optional
from utils.goog_api import get_gmail_service, list_mails, download_attachment_by_msgID, send_email
from cashfree_key import CASHFREE_APP_ID, CASHFREE_SECRET_KEY, CASHFREE_BASE_URL
from flask_cors import CORS, cross_origin
import smtplib
from firedb import db  # This imports your Firestore client
from workflow_bfs import create_graph , execute_graph
# Define the Firestore collection name for workflows
WORKFLOW_COLLECTION = "workflows"

app = Flask(__name__)
mail_service = get_gmail_service()
# Enable CORS for all routes (adjust origins as needed)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ----------------------------
# Other Endpoints
# ----------------------------

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    order_id = data.get('order_id')
    order_amount = data.get('order_amount')
    customer_details = data.get('customer_details')

    headers = {
        'Content-Type': 'application/json',
        'x-client-id': CASHFREE_APP_ID,
        'x-client-secret': CASHFREE_SECRET_KEY
    }

    payload = {
        'order_id': order_id,
        'order_amount': order_amount,
        'order_currency': 'INR',
        'customer_details': customer_details,
        'order_meta': {
            'return_url': f'http://localhost:5173/payment-status?order_id={order_id}'
        }
    }

    response = requests.post(f'{CASHFREE_BASE_URL}/orders', json=payload, headers=headers)
    return jsonify(response.json())

@app.route("/payment-status", methods=["GET"])
def payment_status():
    order_id = request.args.get("order_id")
    headers = {
        'Content-Type': 'application/json',
        'x-client-id': CASHFREE_APP_ID,
        'x-client-secret': CASHFREE_SECRET_KEY
    }
    response = requests.get(f"{CASHFREE_BASE_URL}/orders/{order_id}", headers=headers)
    return jsonify(response.json())

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/get_all_emails/<int:num_mails>", methods=['GET'])
def gib_mails(num_mails: Optional[int] = 5):
    try:
        mails_get = list_mails(mail_service, max_results=num_mails)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify(mails_get)

@app.route("/down_attachment", methods=['POST'])
def attachmentDownload():
    try:
        data = request.json
        msg_id = data.get('message_id')
        download_attachment_by_msgID(service=mail_service, msgID=msg_id)
        return jsonify({"message": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# Workflow Endpoints Using Firebase Firestore
# ----------------------------

@app.route("/save_workflow", methods=["POST", "OPTIONS"])
@cross_origin(origin='*', methods=['POST', 'OPTIONS'], headers=['Content-Type'])
def save_workflow():
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS preflight successful"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200

    data = request.json
    # If no id is provided, assign a unique one.
    if "id" not in data or not data["id"]:
        data["id"] = str(uuid.uuid4())
    try:# Debug: log incoming data
        db.collection(WORKFLOW_COLLECTION).document(data["id"]).set(data)
        print("Workflow saved successfully with id:", data["id"])
        return jsonify({"message": "Workflow saved!", "workflow": data}), 200
    except Exception as e:
        print("Error saving workflow:", e)  # Debug: log error
        return jsonify({"error": str(e)}), 500

@app.route("/get_workflows", methods=["GET"])
@cross_origin()
def get_workflows():
    try:
        workflows_ref = db.collection(WORKFLOW_COLLECTION).stream()
        workflows_list = [{"id": doc.id, **doc.to_dict()} for doc in workflows_ref]
        return jsonify(workflows_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get_workflow/<string:workflow_id>", methods=["GET"])
@cross_origin()
def get_workflow(workflow_id):
    try:
        doc = db.collection(WORKFLOW_COLLECTION).document(workflow_id).get()
        if not doc.exists:
            return jsonify({"error": "Workflow not found"}), 404
        return jsonify({"id": doc.id, **doc.to_dict()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/delete_workflow/<string:workflow_id>", methods=["DELETE", "OPTIONS"])
@cross_origin(origin='*', methods=['DELETE', 'OPTIONS'], headers=['Content-Type'])
def delete_workflow(workflow_id):
    if request.method == "OPTIONS":
        response = jsonify({"message": "CORS preflight successful"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "DELETE, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response, 200

    try:
        doc_ref = db.collection(WORKFLOW_COLLECTION).document(workflow_id)
        if not doc_ref.get().exists:
            return jsonify({"error": "Workflow not found"}), 404
        doc_ref.delete()
        return jsonify({"message": "Workflow deleted"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/execute_workflow/<string:workflow_id>", methods=["POST"])
@cross_origin()
def execute_workflow(workflow_id:str):
    """Executes the latest saved workflow from Firestore."""
    try:
        doc = db.collection(WORKFLOW_COLLECTION).document(workflow_id).get()
        if not db:
            return jsonify({"error": "No workflow found!"}), 400
        # For simplicity, pick the last workflow in the list
        last_workflow = {"id": doc.id, **doc.to_dict()}
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    graph, start_id, node_labels = create_graph(last_workflow)
    execute_graph(graph, start_id, node_labels)
    # nodes = last_workflow.get("nodes", [])
    execution_log = []
    # for node in nodes:
    #     node_label = node["data"]["label"]
    #     if node_label == "Send Email":
    #         recipient = node["data"].get("email", "yash.kambli22@spit.ac.in")
    #         subject = "Subject: Workflow Email"
    #         body = "Hello, this email was sent from the workflow system!"
    #         try:
    #             send_email(mail_service, recipient, subject, body)
    #             execution_log.append({"node": node["id"], "status": "Email Sent", "recipient": recipient})
    #         except Exception as e:
    #             execution_log.append({"node": node["id"], "status": f"Failed: {str(e)}"})
    #     elif node_label == "Receive Email":
    #         try:
    #             fastapi_url = "http://127.0.0.1:8001/read_emails"
    #             response = requests.get(fastapi_url)
    #             if response.status_code == 200:
    #                 execution_log.append({"node": node["id"], "status": "Read Email Task Started"})
    #             else:
    #                 execution_log.append({"node": node["id"], "status": f"Failed: {response.text}"})
    #         except Exception as e:
    #             execution_log.append({"node": node["id"], "status": f"Failed: {str(e)}"})
    return jsonify({"message": "Workflow executed!", "log": execution_log}), 200

# ----------------------------
# FastAPI Integration
# ----------------------------
def run_fastapi():
    """Run FastAPI in a separate thread only once."""
    uvicorn.run(router, host="127.0.0.1", port=8001, log_level="debug")

if __name__ == "__main__":
    # Prevent FastAPI from running twice in Flask's auto-reload
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        threading.Thread(target=run_fastapi, daemon=True).start()
    app.run(debug=True)
