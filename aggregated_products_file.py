from __future__ import print_function
import pickle
import os.path
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/spreadsheets']

def getName(file):
    return file['name'] 

def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    drive_service = build('drive', 'v3', credentials=creds)

    # Call the Drive v3 API

    results = drive_service.files().list(
        fields="files(id, name)", q="'1v-ZSQXTnkD0GPL4aTnugjkOn5DicC_Yz' in parents").execute()
    files = results.get('files', [])

    sortedFiles = sorted(files, key=getName)

    if not files:
        print('No files found.')
        return
    
    print('Sorted files:')
    for file in sortedFiles:
        print(u'{0} - {1}'.format(file['name'], file['id']))


    sheets_service = build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    sheet = sheets_service.spreadsheets()

    for file in sortedFiles:
        time.sleep(10)
        spreadsheet_id = file['id']
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range='Sortiment').execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            print('Supplier:')
            print('%s' % (values[0][0]))

            productRows = values[6:]

            for row in productRows:
                # Print columns A and E, which correspond to indices 0 and 4.
                if len(row) < 5 or len(row[4]) == 0:
                    break
                
                print('%s' % (row[4]))

if __name__ == '__main__':
    main()