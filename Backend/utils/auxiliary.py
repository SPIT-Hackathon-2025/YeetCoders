import requests
import json
import re
from dateutil import parser

def extract_datetime(text):
    # Regular expression to find date and time patterns
    print(text)
    date_patterns = [
        r'\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b',  # Matches formats like 12-09-2024, 12/09/2024
        r'\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b',  # Matches formats like 2024-09-12
        r'\b\d{1,2}\s\w{3,9}\s\d{2,4}\b',  # Matches formats like 12 Sep 2024
        r'\b\w{3,9}\s\d{1,2},\s\d{2,4}\b'  # Matches formats like September 12, 2024
    ]
    
    time_pattern = r'\b\d{1,2}:\d{2}(?::\d{2})?\s?(AM|PM|am|pm)?\b'  # Matches 12:30, 12:30 PM, 23:59:59
    
    extracted_date, extracted_time = None, None
    
    # Extract date
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            extracted_date = match.group()
            break
    
    # Extract time
    match = re.search(time_pattern, text)
    if match:
        extracted_time = match.group()
    
    # Combine and parse into datetime object
    datetime_str = f"{extracted_date or ''} {extracted_time or ''}".strip()
    
    if datetime_str:
        try:
            return parser.parse(datetime_str)
        except:
            return None
    return None

# Example Usage
text = "The meeting is scheduled for September 12, 2024 at 3:45 PM."
print(extract_datetime(text))
def extract_event_details_llm(email_body):
    """
    Uses the Gemini LLM REST API to extract event details from an email.
    The prompt instructs the model to return a JSON object with keys:
      - summary (event title)
      - date (in YYYY-MM-DD format)
      - time (in HH:MM format)
    """
    # Replace with your actual API key.
    GOOGLE_API_KEY = "AIzaSyBezfwnguScLuHejzRqNjnt8X8AGiX69PE"
    
    # Build the endpoint URL with the API key.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    # Construct the prompt.
    prompt = (
        "Extract event details from the following email text. "
        "Return the result as a JSON object with keys 'summary', 'date', and 'time'.\n\n"
        f"Email Text:\n{email_body}\n\n"
        "Example output: {\"summary\": \"Meeting with Bob\", \"date\": \"2025-03-15\", \"time\": \"14:30\"}"
    )
    
    # Build the payload. (This structure mirrors the cURL example you provided.)
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt}
            ]
        }]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Make the POST request to the Gemini API.
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        # Assuming the response returns a JSON object with a "candidates" key,
        # where the first candidate's "output" field contains the generated text.
        result = response.json()
        try:
            candidate = result["candidates"][0]
            generated_text = candidate["output"]
            # Parse the generated text as JSON.
            event_details = json.loads(generated_text)
            return event_details
        except Exception as e:
            raise Exception(f"Error parsing Gemini response: {e}\nResponse content: {result}")
    else:
        raise Exception(f"Gemini API error: {response.status_code} {response.text}")

# Example usage:
if __name__ == "__main__":
    # Example email body; modify this with the actual email text.
    email_body = (
        "Subject: Flight Booking Confirmation\n"
        "Your flight is confirmed!\n"
        "Departure Date: **2024-06-10**\n"
        "Time: **17:15**"
    )
    
    try:
        details = extract_event_details_llm(email_body)
        print("Extracted Event Details:")
        print(json.dumps(details, indent=2))
    except Exception as err:
        print(f"Failed to extract event details: {err}")
