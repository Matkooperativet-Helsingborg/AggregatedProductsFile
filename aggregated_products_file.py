from __future__ import print_function
from datetime import datetime
import constant
import pickle
import os.path
import product_module
import time
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

def get_name(file):
    return file['name'] 

def create_new_aggregated_products_file(drive_service):
    formatted_date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_name = constant.TEMPLATE_NAME_FOR_AGGREGATED_PRODUCT_FILE.format(date_time = formatted_date_time)
    file_metadata = {
        'name': file_name,
        'parents': [constant.DRIVE_FOLDER_ID_FOR_AGGREGATED_PRODUCTS_FILES],
        'mimeType': constant.GOOGLE_SHEET_MIME_TYPE
    }

    file = drive_service.files().create(
        body = file_metadata,
        fields = 'id').execute()
    return file

def save_products_in_new_aggregated_products_file(products, headers, drive_service, sheets_service):
    file = create_new_aggregated_products_file(drive_service)
    print(file)
    file_id = file['id']

    sheet_body = []
    headers_including_supplier = [constant.SUPPLIER] + headers
    sheet_body.append(headers_including_supplier)

    for product in products:
        product_array = product.toArrayIncludingSupplier(headers)
        sheet_body.append(product_array)
	
    range = 'A2'
    value_input_option = constant.GOOGLE_SHEET_VALUE_INPUT_OPTION_TO_USE
    body = {
        'values': sheet_body
    }
    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=file_id, range=range,
        valueInputOption=value_input_option, body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

def parse_product_file_values(values):
    supplier = values[0][0]
    print('Supplier:')
    print('%s' % (supplier))          

    header_row = values[5]
    header_dict = {i: header_row[i] for i in range(len(header_row))}
    
    product_rows = values[6:]
    values_dict_keys = range(len(header_dict))
    products_in_file = []
    
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
        products_in_file.append(product)
    return products_in_file

def parse_product_files(files, sheets_service):
    for file in files:
        print(u'{0} - {1}'.format(file['name'], file['id']))

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
            supplier_products = parse_product_file_values(values)
            products.extend(supplier_products)
    
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
    
    sheets_service = build('sheets', 'v4', credentials=creds)
    print('Sorted files:')
    products = parse_product_files(sorted_files, sheets_service)
    save_products_in_new_aggregated_products_file(
        products, 
        constant.ALL_PRODUCT_FILE_HEADERS,
        drive_service,
        sheets_service)

if __name__ == '__main__':
    main()