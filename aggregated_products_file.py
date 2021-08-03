from __future__ import print_function
import constant
import pickle
import os.path
import product_module
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/spreadsheets']

def get_name(file):
    return file['name'] 

def parse_product_file_values(values):
    supplier = values[0][0]
    print('Supplier:')
    print('%s' % (supplier))          

    header_row = values[5]
    header_dict = {i: header_row[i] for i in range(len(header_row))}
    
    product_rows = values[6:]
    values_dict_keys = range(len(header_dict))
    #values_dict = {key: list() for key in values_dict_keys}
    
    for row in product_rows:
        row_length = len(row)
        if row_length < 5 or len(row[4]) == 0:
            break

        product_info_dict = {}
        
        for col_index in values_dict_keys:

            if col_index < row_length:
                column_value = row[col_index]
            else:
                column_value = None

            header_name = header_dict[col_index]
            product_info_dict[header_name] = column_value

    product_name = product_info_dict[constant.PRODUCT_NAME]
    product = product_module.Product(supplier, product_name, product_info_dict)
    return product

def parse_product_files(files, creds):
    for file in files:
        print(u'{0} - {1}'.format(file['name'], file['id']))


    sheets_service = build('sheets', 'v4', credentials=creds)
    sheet = sheets_service.spreadsheets()
    products = list()

    for file in files:
        time.sleep(10)
        spreadsheet_id = file['id']
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range='Sortiment').execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
        else:
            product = parse_product_file_values(values)
            products.append(product)
    
    return products

def main():
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

    results = drive_service.files().list(
        fields="files(id, name)", q="'1v-ZSQXTnkD0GPL4aTnugjkOn5DicC_Yz' in parents").execute()
    files = results.get('files', [])

    sorted_files = sorted(files, key=get_name)

    if not files:
        print('No files found.')
        return
    
    print('Sorted files:')
    products = parse_product_files(sorted_files, creds)
    print(products)

if __name__ == '__main__':
    main()