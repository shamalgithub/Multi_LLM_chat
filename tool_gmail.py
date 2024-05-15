from __future__ import print_function
import base64
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from email.message import EmailMessage
from googleapiclient.errors import HttpError

import datetime




def view_email_indox(cred):
    service = build('gmail', 'v1', credentials=cred)
    max_results = 100
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=max_results).execute()
    messages = results.get('messages', [])
    unread_email_body = []
    if not messages:
        date_and_time = datetime.datetime.now()
        formatted_date_time = date_and_time.strftime("%Y-%m-%d %H:%M")
        return f"No unread messages as of {formatted_date_time} "
    else:
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            payload = msg['payload']
            headers = payload['headers']
            subject = [header['value'] for header in headers if header['name'] == 'Subject'][0]
            parts = payload.get('parts')
            email_body_parts = []
            if parts:
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        body = part['body']
                        data = body.get('data')
                        if data:
                            text = base64.urlsafe_b64decode(data).decode('utf-8')
                            email_body_parts.append(text)
            email_body_parts = "".join([i for i in email_body_parts])
            unread_email_body.append({
                "EMAIL_SUBJECT":subject,
                "EMAIL_BODY":email_body_parts
            })


def send_email(email_content , email_address , email_subject , auth_creds, email_from ="airesearchtesting@gmail.com" ):
    try:
        service = build("gmail", "v1", credentials=auth_creds)
        message = EmailMessage()
        
        message.set_content(email_content)

        message["To"] = email_address
        message["From"] = email_from
        message["Subject"] = email_subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly",
          "https://www.googleapis.com/auth/gmail.send",]

def create_creds():
  
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                # 'credentials.json', SCOPES)
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds 