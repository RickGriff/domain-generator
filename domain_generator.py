from __future__ import print_function
from builtins import *
import time
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dotenv import load_dotenv

load_dotenv()

# If modifying the scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID") 

# Boilerplate authorization function for Sheets API
def authorize_and_get_credentials():
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
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

## DOMAIN NAME GENERATOR METHODS

# Transform a list rows into a list of columns
def get_columns(table):
    num_cols = len(table[0])
    cols = [ [] for i in range(num_cols) ]

    for row in table:
        for (idx, cell) in enumerate(row):
            cols[idx].append(cell)
    return cols

 # Generate domains names as word combinations from two input lists
def combine_two(list_1, list_2):
    domains = []
    for i in list_1:
        for j in list_2:
            if len(i) > 0 and len(j) > 0:
                domain = i.strip() + j.strip() + ".com"
                domains.append(domain)
    return domains

 # Create a domain names table
def gen_domains(col_a, col_b):
    col_1 = col_a[:]
    col_2 = col_b[:]
 
    title_1 = col_1.pop(0)
    title_2 = col_2.pop(0)

    domains_title = "{}+{}".format(title_1, title_2)
    domains = combine_two(col_1, col_2)

    domains_rows = [domains[i:i+8] for i in range(0, len(domains), 8)] # Convert to array of 8-column rows 
    domains_rows.insert(0, [domains_title]) 
    domains_rows.append([""] * 8) # append an empty row after data

    return domains_rows

 # Generate all possible two-word domain combos from several columns of words
def gen_all_combos(columns):
    domains = []
    for col_i in columns:
        for col_j in columns:
            if col_i != col_j:
                combo = gen_domains(col_i, col_j)
                domains += combo # add the *contents* of combo list to domains list
    return domains

def make_timestamp():
    time_now = time.localtime(time.time())
    
    time_string = "{}:{}:{} {}-{}-{}".format(
        time_now.tm_hour,
        time_now.tm_min,
        time_now.tm_sec,
        time_now.tm_mday,
        time_now.tm_mon,
        time_now.tm_year
        )

    return time_string

def get_input_range():
    input_sheet = input("Please enter an input sheet. Leave blank for default 'RawTerms' sheet.  ")
    input_range = input("Please enter an input range. Leave blank for the default range - A1:H50.  ")

    if input_sheet == "":
        input_sheet = "RawTerms"
    
    if input_range == "":
        input_range = "A1:A50"
    
    input_sheet_and_range = "{}!{}".format(input_sheet, input_range)
    return input_sheet_and_range     

def make_new_sheet(sheet_service, spreadsheet_id, sheet_name):
  # 'requests' in the Sheets API are individual operations to perform on the spreadsheet.
  #  Don't confuse with the actual HTTP request.
    requests = []

    add_sheet_request = {
        'addSheet': {
            'properties': {
                'title': sheet_name,
                'gridProperties': {
                    'rowCount': 20,
                    'columnCount': 12
                },
            }
        }
    }

    requests.append(add_sheet_request)
    data = {'requests': requests}

    response = sheet_service.batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=data).execute()
    return response

def main():
    creds = authorize_and_get_credentials()
    service = build('sheets', 'v4', credentials=creds)
    spreadsheet_id = "1F8gx3Z-Yws_pdW7m-2OiNSzZSBM5gZZttGu9K76YHzQ"

    sheet_service = service.spreadsheets()
    input_range = get_input_range()

    # Grab the raw input table from the sheet via GET request
    result = sheet_service.values().get(spreadsheetId = SPREADSHEET_ID, range="RawTerms2!A1:H50").execute()
    input_table = result.get('values', [])

    columns = get_columns(input_table)

    # Create all two-word domain names
    all_domains = gen_all_combos(columns)

    # Make new sheet that will receive output
    current_time = make_timestamp()
    new_sheet_name = "GenDom {}".format(current_time)
    make_new_sheet(sheet_service, spreadsheet_id, new_sheet_name) # POST request to Sheets API 

    # POST the data to the new sheet
    output_range = "{}!A1:H10000".format(new_sheet_name)
    data = {  'range': output_range, 'values': all_domains}
    
    response = sheet_service.values().update(
    spreadsheetId=spreadsheet_id, range=output_range,
    valueInputOption='RAW', body=data).execute()

    sheet_created = response['updatedRange']

    print('\n')
    print( "Domain names added to following sheet:  {}".format(sheet_created) )
    print('\n')
    # print(response)

if __name__ == '__main__':
    main()

