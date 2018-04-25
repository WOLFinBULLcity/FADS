from mfl.api import *
from model.auction_result import Auction_Result

import pprint
import json

mflTest = Api(2018)

# print(dir(mflTest))

# print(mflTest.nfl_schedule())

# pprint.pprint(mflTest)
#
# pprint.pprint(mflTest.league(26496))

results = mflTest.auction_results(26496)

# auc_res = json.loads(results, object_hook=Auction_Result.as_auction_result)
# dumps = json.dumps(results)

# parsed_json = json.dumps(results)
# pprint.pprint(results)
# pprint.pprint(parsed_json)

completed_auctions = results['auctionResults']

auction = completed_auctions['auctionUnit']

ct = 1
ct_b = 1
ct_c = 1
for a in auction:
  # print('IDK #' + str(ct))
  # print(type(a))
  # pprint.pprint(a)
  ct_b = 1
  for b in a.values():
    print('IDK #' + str(ct) + '.' + str(ct_b))
    # print(type(b))
    # pprint.pprint(b)
    ct_b += 1
    if isinstance(b, list):
      for c in b:
        auct = Auction_Result(c)
        pprint.pprint(c)
        print(auct.winningBid)
        ct_c += 1
  ct += 1

# pprint.pprint(auc_res)

# pprint.pprint(mflTest.players(None,None,True))