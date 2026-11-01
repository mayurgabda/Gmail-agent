import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    # Load credentials directly from token.json
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        raise FileNotFoundError("token.json file is missing from your GitHub repository!")
    return build('gmail', 'v1', credentials=creds)

def list_unread_emails(max_results=10):
    service = get_gmail_service()
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
    messages = results.get('messages', [])
    
    email_summaries = []
    for msg in messages:
        txt = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['From', 'Subject']).execute()
        headers = txt.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        email_summaries.append({'id': msg['id'], 'sender': sender, 'subject': subject})
    return email_summaries

def delete_email(email_id):
    service = get_gmail_service()
    service.users().messages().trash(userId='me', id=email_id).execute()
    return f"Moved email {email_id} to trash."

def forward_email(email_id, recipient_email):
    service = get_gmail_service()
    original = service.users().messages().get(userId='me', id=email_id, format='raw').execute()
    
    message = MIMEText(f"Forwarded message ID {email_id}")
    message['To'] = recipient_email
    message['Subject'] = f"Fwd: Email {email_id}"
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return f"Forwarded email to {recipient_email}"

def compose_email(recipient, subject, body):
    service = get_gmail_service()
    message = MIMEText(body)
    message['To'] = recipient
    message['Subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return f"Email sent to {recipient}"

def unsubscribe_email(email_id):
    service = get_gmail_service()
    msg = service.users().messages().get(userId='me', id=email_id, format='full').execute()
    headers = msg.get('payload', {}).get('headers', [])
    unsub_header = next((h['value'] for h in headers if h['name'].lower() == 'list-unsubscribe'), None)
    
    service.users().messages().trash(userId='me', id=email_id).execute()
    return f"Unsubscribed/Trashed email ID {email_id}. Header found: {bool(unsub_header)}"
