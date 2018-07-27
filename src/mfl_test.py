# !/usr/local/bin/python

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from mfl.api import Api
from model.auction_data import Auction_Data
from model.league_data import League_Data
from model.player_pool import Player_Pool
from oauth2client import file, client, tools

import config
import datetime
import os
import pickle
import pprint

player_pool_file = './pickle/player_pool_file.pickle'
league_data_file = './pickle/league_data_file.pickle'
mfl_api = Api(config.LEAGUE_CONFIG['year'])

now = datetime.datetime.now()
today = now.strftime('%m/%d/%Y')

def get_player_pool():
  player_info = mfl_api.players(details=True)
  return Player_Pool(
      last_update=today,
      players=player_info['players']['player'],
      positions=config.ELIGIBILITY_CONFIG['eligible_positions'],
      years=config.ELIGIBILITY_CONFIG['eligible_years']
  )

def get_league_data():
  league_info = mfl_api.league(config.LEAGUE_CONFIG['id'])
  return League_Data(
      last_update=today,
      conferences=league_info['league']['conferences']['conference'],
      divisions=league_info['league']['divisions']['division'],
      franchises=league_info['league']['franchises']['franchise']
  )

# Check if we have a player pool saved
if os.path.isfile(player_pool_file):
  with open(player_pool_file, 'rb') as f:
    pp = pickle.load(f)
else:
  # Create the instance of our Player Pool
  pp = get_player_pool()

# Check if we have league data saved
if os.path.isfile(league_data_file):
  with open(league_data_file, 'rb') as f:
    ld = pickle.load(f)
else:
  # Create the instance of our League Data
  ld = get_league_data()

# Check if the player pool needs an update
if today > pp.last_update:
  pp = get_player_pool()

# Check if our league data needs an update
if today > ld.last_update:
  ld = get_league_data()

# Setup the Sheets API
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
  flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
  creds = tools.run_flow(flow, store)
service = build('sheets', 'v4', http=creds.authorize(Http()))
VALUE_INPUT_OPTION = 'USER_ENTERED'

def update_player_pools():
  # Call the Sheets API
  for conference_id, conference in ld.conferences.items():
    for position in config.ELIGIBILITY_CONFIG['eligible_positions']:
      SPREADSHEET_ID = config.NOMINATION_SHEETS[conference_id]

      pos_ref = '{}s'.format(position)
      pos_list = getattr(pp, pos_ref)

      RANGE_NAME = '{}{}'.format(
          pos_ref,
          config.NOMINATION_SHEET_CONFIG['cell_range']
      )
      default = 'N/A'

      values = []
      for player_id, player in pos_list.items():
        first_copy_top_bid = ''
        second_copy_top_bid = ''

        # pa = ad.auctions_for_player(
        #     conference_id=conference_id,
        #     player_id=player_id
        # )
        # if pa is not None:
        #   if pa[0]['status'] == 'closed':
        #     first_copy_top_bid = '${}'.format(pa[0]['top_bid'])
        #
        #     if len(pa) > 1 and pa[1]['status'] == 'closed':
        #       second_copy_top_bid = '${}'.format(pa[1]['top_bid'])

        # aav = ad.average_price_for_player(player_id=player_id)
        # aav_str = '' if aav is None else '${}'.format(aav)

        values.append(
            [
              player.get('position', default),
              player.get('name', default),
              player.get('eligibility', default),
              first_copy_top_bid,
              second_copy_top_bid,
              '',
              player.get('birthdate_formatted', default),
              player.get('age', default),
              player.get('team', default),
              player.get('college', default),
              player_id
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
      print('{0}: {1} cells updated.'.format(
          conference.get('name'),
          result.get('updatedCells'))
      )

def update_scholarship_trackers():
  # Call the Sheets API
  for franchise_id, franchise in ld.franchises.items():
    conference_id = ld.conference_id_from_franchise_id(franchise_id)
    SPREADSHEET_ID = config.SCHOLARSHIP_TRACKER_SHEETS[conference_id]

    team_ref = '{}'.format(franchise.get('name'))

    RANGE_NAME = '{}{}'.format(
        team_ref,
        config.SCHOLARSHIP_TRACKER_CONFIG['cell_range']
    )

    default = 'N/A'
    auction_info = ad.auctions_for_franchise(franchise_id)

    values = []
    for player_id, auction in auction_info.items():
      player = pp.eligible_players[player_id]
      # {Position: QB, Player: Deshaun Watson, Year: FR, Scholarship: 50, Notes: r17}
      values.append(
          [
            player.get('position', default),
            player.get('display_name', default),
            player.get('eligibility', default),
            '${}'.format(auction.get('top_bid')),
            '-'
          ]
      )
    body = {
      'range': RANGE_NAME,
      'majorDimension': 'ROWS',
      'values': values
    }

    try:
      result = service.spreadsheets().values().update(
          spreadsheetId=SPREADSHEET_ID,
          range=RANGE_NAME,
          valueInputOption=VALUE_INPUT_OPTION,
          body=body).execute()
    except:
      print('Error updating sheet range {}. Skipping'.format(RANGE_NAME))
  print("Scholarship Trackers update completed.")


transactions = mfl_api.transactions(
    league_id=config.LEAGUE_CONFIG['id']
)['transactions']['transaction']

# print(type(transactions))

# rt = transactions[::-1]
#
# print('Found {} transactions; Reversed: {}'.format(
#     len(transactions),
#     len(rt)
# ))
# pprint.pprint(transactions)

ad = Auction_Data(ld=ld, transactions=transactions)

# ad.conference_totals()

# update_player_pools()


# player_name = 'Hunter Henry'
# ad.auctions_for_player_name(player_pool=pp, player_name=player_name)


# dudes = pp.player_search({'display_name': 'Tyler Lockett'})
# for dude_id, dude in dudes.items():
#   print('Name: {}; Pos: {}; Drafted: {}; College: {}; Team: {}; ID: {}'.format(
#       dude.get('name'),
#       dude.get('position'),
#       dude.get('draft_year'),
#       dude.get('college'),
#       dude.get('team'),
#       dude_id
#   ))

# dudes = pp.player_search({'college': 'North Carolina State'})
# for dude_id, dude in dudes.items():
#   print('Name: {}; Pos: {}; Drafted: {}; College: {}; Team: {}; ID: {}'.format(
#       dude.get('name'),
#       dude.get('position'),
#       dude.get('draft_year'),
#       dude.get('college'),
#       dude.get('team'),
#       dude_id
#   ))

dudes = pp.player_search(
    params={
      'college': 'Oklahoma State',
      'team': 'PIT'
    },
    target=pp.eligible_players,
    expression='OR'
)
for dude_id, dude in dudes.items():
  print('Name: {}; Pos: {}; Drafted: {}; College: {}; Team: {}; ID: {}'.format(
      dude.get('name'),
      dude.get('position'),
      dude.get('draft_year'),
      dude.get('college'),
      dude.get('team'),
      dude_id
  ))

# Save records
with open(player_pool_file, 'wb') as f:
  pickle.dump(pp, f)
with open(league_data_file, 'wb') as f:
  pickle.dump(ld, f)

