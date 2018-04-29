# !/usr/local/bin/python

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from mfl.api import Api
from model.player_pool import Player_Pool
from oauth2client import file, client, tools

import datetime
import dpath.util
import os
import pickle
import pprint

player_list_file = './pickle/player_pool_file.pickle'
mfl_api = Api(2018)

eligible_positions = ['QB', 'RB', 'WR', 'TE']
eligible_years = {
  '2018': 'FR',
  '2017': 'SO',
  '2016': 'JR',
  '2015': 'SR'
}

now = datetime.datetime.now()
today = now.strftime('%m/%d/%Y')

def get_player_pool():
  player_result = mfl_api.players(details=True)
  return Player_Pool(
      last_update=today,
      players=player_result['players']['player'],
      positions=eligible_positions,
      years=eligible_years
  )

# Check if we have a player pool saved
if os.path.isfile(player_list_file):
  with open(player_list_file, 'rb') as f:
    pp = pickle.load(f)
else:
  # Create the instance of our Player Pool
  player_result = mfl_api.players(details=True)
  pp = get_player_pool()

# Check if the player pool needs an update
if today > pp.last_update:
  pp = get_player_pool()

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
  flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
  creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))

# Call the Sheets API
SPREADSHEET_ID = '1UjAaJzIbqkYEpDzn0PQB3KQTD8wSdSXg3hsOW-6WOac'
VALUE_INPUT_OPTION = 'USER_ENTERED'

for position in eligible_positions:
  pos_ref = '{}s'.format(position)
  pos_list = getattr(pp, pos_ref)

  RANGE_NAME = '{}!A3:F1000'.format(pos_ref)

  values = []
  for player in pos_list:
    # Position | Player Name | Eligibility Year | NFL Team | College Team | MFL ID
    values.append(
        [
          player.get('position'),
          player.get('name'),
          player.get('eligibility'),
          player.get('team'),
          player.get('college'),
          player.get('id')
        ]
    )
  body = {
    'range': RANGE_NAME,
    'majorDimension': 'ROWS',
    'values': values
  }
  result = service.spreadsheets().values().update(
      spreadsheetId=SPREADSHEET_ID,
      range=RANGE_NAME,
      valueInputOption=VALUE_INPUT_OPTION,
      body=body).execute()
  print('{0} cells updated.'.format(result.get('updatedCells')))

search_results = pp.player_search({
  'id': '13613',
  'name': 'Gurley, Todd',
  'college': 'North Carolina State'
}, 'OR')
pprint.pprint(search_results)


# results = mfl_api.auction_results(26496)
#
# leagues = dpath.util.values(results, "auctionResults/auctionUnit/*/unit")
# drafts = dpath.util.values(results, "auctionResults/auctionUnit/*/auction")
#
# sort_on = 'name'
# pl.players = sorted(pl.players, key=lambda item: item[sort_on])
# # pprint.pprint(data_sorted)
# pprint.pprint(pl.players)

# pprint.pprint(result)

# for idx in range(len(leagues)):
#   # print(leagues[idx])
#   # print(drafts[idx])
#   # print("Players from Auction #" + str(idx))
#   for auction in drafts[idx]:
#     if isinstance(auction, dict):
#       player_id = auction['player']
#       player_info = mfl_api.players(
#           players=[player_id],
#           details=True
#       )['players']['player']
#
#       player_name = player_info['name']
#       player_pos = player_info['position']
#
#       # print(player_info)
#
#       # print(auction)
#       #
#       # print(
#       #     "Player ID: " + player_id + ", " +
#       #     "Player Name: " + player_name + ", " +
#       #     "Player Position: " + player_pos
#       # )
#
#       # franchise_id = auction['franchise']
#       # franchise_info = mflTest.league(
#       #     league_id=26496,
#       #     franchise_id=franchise_id
#       # )
#       #
#       # print(franchise_info)


# ct = 1
# ct_b = 1
# ct_c = 1
# for draft in auction:
#   print('IDK #' + str(ct))
#   ct_b = 1
#   pprint.pprint(draft.keys())
#
#   conference = draft['unit']
#   completed_auctions = draft['auction']
#
  # for b in conference_draft.values():
  #   # print(type(b))
  #   ct_b += 1
  #   if isinstance(b, list):
  #     for c in b:
  #       auct = Auction_Result(c)
  #       # pprint.pprint(c)
  #       # print(auct.winningBid)
  #       ct_c += 1
  # ct += 1

# pprint.pprint(auc_res)

# pprint.pprint(mflTest.players(None,None,True))

# Save records
with open(player_list_file, 'wb') as f:
  pickle.dump(pp, f)
