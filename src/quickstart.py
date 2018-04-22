"""
Shows basic usage of the Sheets API. Prints values from a Google Spreadsheet.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
  flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
  creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

# Call the Sheets API
# SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
#RANGE_NAME = 'Class Data!A2:E'

SPREADSHEET_ID = '1UjAaJzIbqkYEpDzn0PQB3KQTD8wSdSXg3hsOW-6WOac'
RANGE_NAME = 'Boston College!B4:F24'

VALUE_INPUT_OPTION = 'USER_ENTERED'

# {Position: QB, Player: Deshaun Watson, Year: FR, Scholarship: 50, Notes: r17}
values = [
  # Cell values ...
  ['QB', 'Lamar Jackson', 'FR', '99', '-'],
  ['RB', 'Leonard Fournette', 'FR', '37', 'r17'],
  ['WR', 'Sammy Watkins', 'SR', '1', 'r14'],
]
body = {
  'range': RANGE_NAME,
  'majorDimension': 'ROWS',
  'values': values
}
result = service.spreadsheets().values().append(
    spreadsheetId=SPREADSHEET_ID,
    range=RANGE_NAME,
    valueInputOption=VALUE_INPUT_OPTION,
    body=body).execute()
print('{0} cells appended.'.format(result \
                                   .get('updates') \
                                   .get('updatedCells')));

# result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
#                                              range=RANGE_NAME).execute()
# values = result.get('values', [])
# if not values:
#   print('No data found.')
# else:
#   headers = values.pop(0)
#   for row in values:
#     # Print columns A and E, which correspond to indices 0 and 4.
#     str = '{'
#     for col in range(len(row)):
#       if col > 0:
#         str += ', '
#       str += headers[col] + ': ' + row[col]
#     str += '}'
#     print(str)