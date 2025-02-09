import os,datetime
from pathlib import Path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from email.mime.text import MIMEText
import base64
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/calendar"
          ]
file_path = Path(__file__).parent.absolute()
creds_path = file_path  / "credentials.json"
# Folder to save attachments
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Create folder if it doesn't exist

def get_gmail_service():
    """Authenticate and return a Gmail API service instance."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)
def get_calendar_service():
    """Authenticate and return a Google Calendar API service instance."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)
def create_calendar_event(service, summary, description, start_time, end_time):
    """Create an event in the Google Calendar."""
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time, "timeZone": "UTC"},
        "end": {"dateTime": end_time, "timeZone": "UTC"},
    }
    created_event = service.events().insert(calendarId="primary", body=event).execute()
    print(f"✅ Event Created: {created_event.get('htmlLink')}")
    return created_event.get("id")

def list_calendar_events(service, max_results=10):
    """Fetch upcoming events from the Google Calendar API."""
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    events_result = (
        service.events()
        .list(calendarId="primary", timeMin=now, maxResults=max_results, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events = events_result.get("items", [])

    event_list = []
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        event_list.append({"summary": event.get("summary", "No Title"), "start": start})
    
    return event_list

def list_mails_new(service, max_results=5, query=""):
    """Fetch and return emails with an optional query (e.g., after:YYYY/MM/DD)."""
    results = service.users().messages().list(
        userId="me", maxResults=max_results, q=query
    ).execute()
    
    messages = results.get("messages", [])
    email_list = []

    if not messages:
        print("No emails found.")
        return []

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = msg_data["payload"].get("headers", [])
        
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        
        # Extract internalDate (in milliseconds)
        internal_date = int(msg_data.get("internalDate", 0))
        
        email_list.append({
            "subject": subject,
            "sender": sender,
            "message_id": msg["id"],
            "internal_date": internal_date,  # Store internal date for reference
        })

    return email_list


def list_mails(service, max_results=5, query=""):
    """Fetch and return emails with an optional query, including the email body."""
    results = service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
    messages = results.get('messages', [])
    email_list = []
    
    if not messages:
        print("No emails found.")
        return []
    
    print(f"Listing {max_results} recent emails:\n" + "=" * 50)
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload'].get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        internal_date = int(msg_data.get("internalDate", 0))
        body = get_email_body(msg_data)
        
        email_list.append({
            'subject': subject,
            'sender': sender,
            'message_id': msg['id'],
            'internal_date': internal_date,
            'body': body
        })
        
        print(f"From: {sender}")
        print(f"Subject: {subject}")
        print(f"Message ID: {msg['id']}")
        print("=" * 50)
    
    return email_list


def download_attachments(service, max_results=5):
    """Fetch emails and download attachments."""
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No emails found.")
        return

    print(f"Downloading attachments from {max_results} emails:\n" + "=" * 50)

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()

        # Check if email has attachments
        if 'parts' in msg_data['payload']:
            for part in msg_data['payload']['parts']:
                if part.get('filename'):  # Only process files
                    attachment_id = part['body'].get('attachmentId')
                    if attachment_id:
                        attachment = service.users().messages().attachments().get(
                            userId='me', messageId=msg['id'], id=attachment_id
                        ).execute()
                        
                        file_data = base64.urlsafe_b64decode(attachment['data'])
                        file_path = os.path.join(DOWNLOAD_FOLDER, part['filename'])
                        
                        with open(file_path, "wb") as f:
                            f.write(file_data)
                        
                        print(f"Downloaded: {part['filename']} ✅")

    print("Attachment download complete!")

def send_email(service, to, subject, body):
    """✅ Sends an email using Gmail API."""
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        print(f"✅ Email Sent to {to}")
    except Exception as e:
        print(f"❌ Failed to send email: {str(e)}")
        
def get_email_body(msg_data):
    """
    Recursively extracts and decodes the plain text email body from a Gmail API message payload.
    It searches for a 'text/plain' part and decodes it from Base64.
    """
    def extract_from_payload(payload):
        # If the payload has a MIME type of text/plain and contains data, decode it.
        if payload.get("mimeType") == "text/plain" and "data" in payload.get("body", {}):
            data = payload["body"]["data"]
            try:
                return base64.urlsafe_b64decode(data).decode("utf-8")
            except Exception as e:
                print(f"Error decoding email body: {e}")
                return ""
        # If the payload contains parts, iterate through them.
        elif "parts" in payload:
            for part in payload["parts"]:
                # Prefer parts with MIME type 'text/plain'
                if part.get("mimeType") == "text/plain":
                    result = extract_from_payload(part)
                    if result:
                        return result
            # Fallback: try to extract from any part.
            for part in payload["parts"]:
                result = extract_from_payload(part)
                if result:
                    return result
        return ""
    
    payload = msg_data.get("payload", {})
    return extract_from_payload(payload)
def get_drive_service():
    """Authenticate and return a Google Drive API service instance."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)
def upload_all_downloads_to_drive(folder_id=None):
    """✅ Upload all files from `downloads/` to Google Drive."""
    drive_service = get_drive_service()

    for filename in os.listdir(DOWNLOAD_FOLDER):
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)

        if os.path.isfile(file_path):  # ✅ Ensure it's a file, not a folder
            upload_to_drive(file_path, folder_id)

def upload_to_drive(file_path, folder_id=None):
    """Uploads a file to Google Drive and returns the file ID."""
    drive_service = get_drive_service()

    file_metadata = {"name": os.path.basename(file_path)}
    if folder_id:
        file_metadata["parents"] = [folder_id]  # Upload to a specific folder

    media = MediaFileUpload(file_path, resumable=True)

    file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    print(f"✅ Uploaded {file_path} to Google Drive, File ID: {file.get('id')}")
    return file.get("id")

def download_attachment_by_msgID(service, msgID):
    """Download attachments from a specific email using the message ID."""
    try:
        # Fetch the email message based on the provided msgID
        msg_data = service.users().messages().get(userId='me', id=msgID).execute()

        # Check if email has attachments
        if 'parts' in msg_data['payload']:
            for part in msg_data['payload']['parts']:
                if part.get('filename'):  # Only process files
                    attachment_id = part['body'].get('attachmentId')
                    if attachment_id:
                        # Fetch the attachment using the attachmentId
                        attachment = service.users().messages().attachments().get(
                            userId='me', messageId=msgID, id=attachment_id
                        ).execute()
                        
                        # Decode the file data
                        file_data = base64.urlsafe_b64decode(attachment['data'])
                        
                        # Save the attachment to the DOWNLOAD_FOLDER
                        file_path = os.path.join(DOWNLOAD_FOLDER, part['filename'])
                        
                        with open(file_path, "wb") as f:
                            f.write(file_data)
                        
                        print(f"Downloaded: {part['filename']} ✅")
        else:
            print("No attachments found in this email.")
    except Exception as e:
        print(f"An error occurred while downloading the attachment: {e}")

if __name__ == '__main__':
    gmail_service = get_gmail_service()
    
    # List emails
    list_mails(gmail_service, max_results=5)
    
    # Download attachments
    download_attachments(gmail_service, max_results=5)
