import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import os

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify', 
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/gmail.readonly',
    # 'https://www.googleapis.com/auth/gmail.metadata'
    ]

def get_user_email(service):
    user_profile = service.users().getProfile(userId='me').execute()
    email_address = user_profile['emailAddress']
    return email_address


def delete_emails(service, user_id, limit=350):
    limit = int(limit) 
    print("Entered delete_emails function")
    try:
        counter = 0
        page_token = None

        while counter < limit:
            response = service.users().messages().list(userId=user_id, pageToken=page_token, 
                                                      q="-is:starred older_than:7d").execute()
            messages = response.get('messages', [])

            if not messages:
                print("No more messages to process")
                break

            for message in messages:
                if counter >= limit:
                    print("Reached the limit, stopping process")
                    break

                message_id = message['id']
                service.users().messages().delete(userId=user_id, id=message_id).execute()
                print(f"Deleted message ID: {message_id}")
                counter += 1

            page_token = response.get('nextPageToken')
            if not page_token:
                break

    except Exception as error:
        print(f'An error occurred in delete_emails: {type(error).__name__}: {error}')


    # except Exception as error:
    #     print(f'An error occurred in delete_emails: {error}')  # Debugging print

def get_service():
    print("Acquiring credentials and building service")  # Debugging print
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        print("token.json not found, need to authenticate")  # Debugging print
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("Saved new token to token.json")  # Debugging print

    return build('gmail', 'v1', credentials=creds)

def lambda_handler(event, context):
    print("Starting lambda_handler")  # Debugging print
    service = get_service()
    delete_emails(service, 'me', '350')
    print("lambda_handler execution completed")  # Debugging print
    return {
        'statusCode': 200,
        'body': 'Emails processed successfully'
    }


def main():
    print("Running script locally") 
    service = get_service()

    # Get user email
    user_email = get_user_email(service)
    print(f"Deleting emails from account: {user_email}")  

    # Continue with deletion logic
    delete_emails(service, 'me', '350')

if __name__ == '__main__':
    main()

