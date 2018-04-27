from mfl.api import *
from model.auction_result import Auction_Result

import pprint
import json
import dpath.util

mflTest = Api(2018)

# print(dir(mflTest))

# print(mflTest.nfl_schedule())

# pprint.pprint(mflTest)
# pprint.pprint(mflTest.league(26496))

results = mflTest.auction_results(26496)

# auc_res = json.loads(results, object_hook=Auction_Result.as_auction_result)
# dumps = json.dumps(results)

# parsed_json = json.dumps(results)
# pprint.pprint(results)
# pprint.pprint(parsed_json)

# completed_auctions = results['auctionResults']
#
# auction = completed_auctions['auctionUnit']

# something = [x['auction'] for x in results['auctionResults']['auctionUnit'].values()]
# pprint.pprint(results['auctionResults']['auctionUnit'][0]['unit'])

leagues = dpath.util.values(results, "auctionResults/auctionUnit/*/unit")
drafts = dpath.util.values(results, "auctionResults/auctionUnit/*/auction")

# print(results)

for idx in range(len(leagues)):
  # print(leagues[idx])
  # print(drafts[idx])
  # print("Players from Auction #" + str(idx))
  for auction in drafts[idx]:
    if isinstance(auction, dict):
      player_id = auction['player']
      player_info = mflTest.players(
          players=[player_id],
          details=True
      )['players']['player']

      player_name = player_info['name']
      player_pos = player_info['position']

      # print(player_info)

      # print(auction)
      #
      # print(
      #     "Player ID: " + player_id + ", " +
      #     "Player Name: " + player_name + ", " +
      #     "Player Position: " + player_pos
      # )

      # franchise_id = auction['franchise']
      # franchise_info = mflTest.league(
      #     league_id=26496,
      #     franchise_id=franchise_id
      # )
      #
      # print(franchise_info)

# player_object = mflTest.players(players=[13128])
# pprint.pprint(player_object)

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