from fastapi import FastAPI, HTTPException
from utils.goog_api import list_mails,get_calendar_service,create_calendar_event,list_calendar_events,list_mails_new, get_gmail_service, send_email, download_attachment_by_msgID, upload_all_downloads_to_drive
import logging
import requests
import re
from datetime import timedelta
from utils.auxiliary import extract_datetime,extract_event_details_llm
import asyncio
from utils.slack_help import send_slack_message
from datetime import datetime, timezone
calendar_service = get_calendar_service()
router = FastAPI()
mail_service = get_gmail_service()

# Store server start time and last fetched email ID
server_start_time = None
last_email_id = None

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

@router.on_event("startup")
async def startup_event():
    """Initialize server start time when FastAPI starts"""
    global server_start_time
    server_start_time = datetime.now(timezone.utc)
    logging.info(f"Server started at: {server_start_time}")

@router.get('/read_emails')
async def fetch_new_emails():
    global last_email_id
    logging.info("📩 FastAPI: Checking for new emails...")
    emails = list_mails(mail_service, max_results=5)

    
    # Filter emails based on server start time
    new_emails = []
    for email in emails:
        # Convert email timestamp to datetime
        email_time = datetime.fromtimestamp(
            int(email.get('internal_date', 0)), 
            timezone.utc
        )
        
        # Only include emails after server start
        if email_time > server_start_time:
            if last_email_id is None or email["message_id"] != last_email_id:
                new_emails.append(email)
            else:
                break

    if new_emails:
        last_email_id = new_emails[0]["message_id"]
        logging.info(f"📩 FastAPI: {len(new_emails)} NEW Emails Fetched: {new_emails}")
        return {"new_emails": new_emails}
    else:
        logging.info("📩 FastAPI: No new emails since server start.")
        return {"message": "No new emails since server start"}


# Set server start time (UTC)
server_start_time = datetime.now(timezone.utc)
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

@router.on_event("startup")
async def startup_event():
    logging.info(f"Server started at: {server_start_time.isoformat()}")


@router.get("/process_email_llm_for_event")
async def process_email_for_event():
    """
    Fetch the latest email, use Gemini LLM to extract event details,
    and then create a Calendar event.
    """
    emails = list_mails(mail_service, max_results=1)
    if not emails:
        return {"message": "No emails found"}

    email_body = emails[0].get("body", "")
    
    # Use Gemini LLM to extract event details from the email body.
    try:
        event_data = extract_event_details_llm(email_body)
    except Exception as e:
        logging.error(f"LLM extraction failed: {e}")
        return {"message": f"LLM extraction failed: {e}"}
    
    # Check that the necessary fields are present.
    if not event_data.get("date") or not event_data.get("time"):
        logging.info("Could not extract date or time from email")
        return {"message": "Could not extract date or time from email"}
    
    # Construct ISO format start and end times (assuming event lasts one hour).
    start_time = f"{event_data['date']}T{event_data['time']}:00Z"
    # Simple logic: add one hour to the hour component of the time.
    hour = int(event_data["time"][:2]) + 1
    end_time = f"{event_data['date']}T{hour:02}{event_data['time'][2:]}:00Z"
    
    # Create a calendar event.
    event_id = create_calendar_event(
        calendar_service,
        event_data["summary"],
        "Auto-created event",
        start_time,
        end_time
    )
    
    return {"message": "Event created", "event_id": event_id}
@router.get("/process_email_for_event")
async def process_email_for_event():
    """
    Fetch the latest email, extract event datetime details using extract_datetime(),
    and create a Calendar event with a 1-hour duration.
    """
    emails = list_mails(mail_service, max_results=1)
    if not emails:
        raise HTTPException(status_code=404, detail="No emails found")
    
    email_body = emails[0].get("body", "")
    if not email_body:
        raise HTTPException(status_code=404, detail="Email body is empty")
    
    event_dt = extract_datetime(email_body)
    print("Extracted datetime:", event_dt)
    if not event_dt:
        return {"message": "Could not extract date/time from email"}
    
    # Format start and end times in ISO format (assuming UTC)
    start_time = event_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time = (event_dt + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Extract a subject from the email body for the event summary.
    subject_match = re.search(r"^Subject:\s*(.*)$", email_body, re.IGNORECASE | re.MULTILINE)
    summary = subject_match.group(1).strip() if subject_match else "No Subject"
    
    # Create the calendar event (ensure create_calendar_event is defined appropriately)
    event_id = create_calendar_event(
        calendar_service,
        summary,
        "Auto-created event",
        start_time,
        end_time
    )
    
    return {"message": "Event created", "event_id": event_id}

@router.get("/uploader_of_attachments")
async def upload_attachments():
    upload_all_downloads_to_drive()
    return {"message": "success"}

@router.get("/downloader_of_attachments")
async def download_attachmentsss():
    newest_mail = list_mails(mail_service, 1)
    if newest_mail:
        download_attachment_by_msgID(mail_service, msgID=newest_mail[0]['message_id'])
        return {"message": "success"}
    return {"message": "no emails found"}