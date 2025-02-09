import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SLACK_BOT_TOKEN="xoxb-8416780939462-8436101915585-ZhhbxhBgu2skb0tdtxR9ttJB"
SLACK_CHANNEL_ID="C08CCGT5M53"
# Slack Bot Token & Channel ID (stored securely in .env)
# SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
# SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

def send_slack_message(message: str):
    """
    Sends a message to a Slack channel.

    :param message: The text message to send.
    :return: Success or error response.
    """
    if not SLACK_BOT_TOKEN or not SLACK_CHANNEL_ID:
        return {"error": "Slack credentials are missing."}

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": SLACK_CHANNEL_ID,
        "text": message
    }

    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    if response_data.get("ok"):
        return {"success": "Message sent to Slack"}
    else:
        return {"error": response_data.get("error", "Failed to send message")}

# Example usage:
# print(send_slack_message("This is a test message from Flask!"))