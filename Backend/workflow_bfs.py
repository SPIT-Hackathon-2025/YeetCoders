from collections import deque
from utils.goog_api import get_gmail_service, list_mails, download_attachment_by_msgID, send_email
import requests,time
mail_service = get_gmail_service()
from utils.slack_help import send_slack_message
def check_condition(condition):
    pass


def execute_action(action):

    node_label = action["label"]
    execution_log = []
    print(f"THis is Real action:- {node_label}")
    if node_label == "Send Email":
        recipient = action.get("email", "macaronimutton@gmail.com")  # ✅ Dynamic email
        subject = action.get("subject", "hiasdahhahgsdjbazmnahasd asd ad")
        body = action.get("body", "Hello, this email was aosjdkjshdfjsh sent from the workflow system!")

        try:
            send_email(mail_service, recipient, subject, body)
            execution_log.append({"node": action["label"], "status": "Email Sent", "recipient": recipient})
        except Exception as e:
            execution_log.append({"node": action["label"], "status": f"Failed: {str(e)}"})
    elif node_label == "Receive Email":
            try:
                fastapi_url = "http://127.0.0.1:8001/read_emails"
                response = requests.get(fastapi_url)
                if response.status_code == 200:
                    execution_log.append({"node": action["label"], "status": "Read Email Task Started"})
                else:
                    execution_log.append({"node": action["label"], "status": f"Failed: {response.text}"})
            except Exception as e:
                execution_log.append({"node": action["label"], "status": f"Failed: {str(e)}"})
    elif node_label == "Download attachments":
            try:
                fastapi_url = "http://127.0.0.1:8001/downloader_of_attachments"
                response = requests.get(fastapi_url)
                if response.status_code == 200:
                        execution_log.append({"node": action["label"], "status": "Download Email started"})
                else:
                    execution_log.append({"node": action["label"], "status": f"Failed: {response.text}"})
            except Exception as e:
                execution_log.append({"node": action["label"], "status": f"Failed: {str(e)}"})
    elif node_label == "Upload File":
            try:
                fastapi_url = "http://127.0.0.1:8001/uploader_of_attachments"
                response = requests.get(fastapi_url)
                if response.status_code == 200:
                        execution_log.append({"node": action["label"], "status": "Upload Email started"})
                else:
                    execution_log.append({"node": action["label"], "status": f"Failed: {response.text}"})
            except Exception as e:
                execution_log.append({"node": action["label"], "status": f"Failed: {str(e)}"})
    elif node_label == "Slack Notification":
        message = action.get("message", "Default Slack Notification from Workflow Automation")

        try:
            slack_response = send_slack_message(message)
            if "success" in slack_response:
                execution_log.append({"node": action["label"], "status": "Slack Notification Sent"})
            else:
                execution_log.append({"node": action["label"], "status": f"Failed: {slack_response['error']}"})
        except Exception as e:
            execution_log.append({"node": action["label"], "status": f"Failed: {str(e)}"})
    elif node_label == "Create Calender":
            try:
                fastapi_url = "http://127.0.0.1:8001/process_email_for_event"
                response = requests.get(fastapi_url)
                if response.status_code == 200:
                        execution_log.append({"node": action["label"], "status": "Added Calender event"})
                else:
                    execution_log.append({"node": action["label"], "status": f"Failed: {response.text}"})
            except Exception as e:
                execution_log.append({"node": action["label"], "status": f"Failed: {str(e)}"})

def create_graph(workflow):
    nodes = workflow.get('nodes', [])
    node_labels = {node['id']: node['data'] for node in nodes}
    print(node_labels)
    start_id = '1'
    for k,v in node_labels.items():
        if v['label']=="Start":
            start_id = k
            break
    edges = workflow.get('edges', [])
    edges_list = [[edge['source'], edge['target']] for edge in edges]
    graph = {}
    for edge in edges_list:
        if edge[0] not in graph:
            graph[edge[0]] = []
        if edge[1] not in graph:
            graph[edge[1]] = []
        graph[edge[0]].append(edge[1])
    
    return graph, start_id, node_labels

def execute_graph(graph, start_id, node_labels):
    while True:
        queue = deque()
        queue.append(start_id)
        visited = set()
        visited.add(start_id)
        while queue:
            length = len(queue)
            for i in range(length):
                node = queue.popleft()

                if node_labels[node]['label'].startswith("If"):
                    if not check_condition(node_labels[node]):
                        continue
                else:
                    execute_action(node_labels[node])

                for neighbor in graph[node]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
        time.sleep(60)
    
