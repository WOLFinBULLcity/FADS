# !/usr/local/bin/python

from model.league_data import League_Data

import itertools
import pprint


class Auction_Data:

  def __init__(self, ld: League_Data, transactions: dict):
    self.ld: League_Data = ld
    self.transactions: dict = transactions

    self.conference_auctions = {c: {} for c in ld.conferences}

    for t in reversed(transactions):
      if t['type'] not in ['AUCTION_BID', 'AUCTION_WON']:
        continue

      c_id = self.ld.conference_id_from_franchise_id(t['franchise'])

      transaction = t.pop('transaction')
      p_id, raw_amount, discard = transaction.split('|')
      t['amount'] = ''.join(itertools.takewhile(str.isdigit, raw_amount))

      # Is this a nomination?
      if t['amount'] == '1':
        auction_init = {
          'status': 'active',
          'top_bid': t['amount'],
          'nominator': t['franchise'],
          'bid_list': []
        }

        # Is this the first copy?
        if p_id not in self.conference_auctions[c_id]:
          self.conference_auctions[c_id][p_id] = [auction_init]
        else:
          self.conference_auctions[c_id][p_id].append(auction_init)

      # Use shorter variable pointer for readability
      p_auction = self.conference_auctions[c_id][p_id]
      idx = len(p_auction) - 1

      default = '0'

      if int(t['amount']) > int(p_auction[idx].get('top_bid', default)):
        p_auction[idx]['top_bid'] = t['amount']

      p_auction[idx]['bid_list'].append(t)

      if t['type'] == 'AUCTION_WON':
        p_auction[idx]['status'] = 'closed'



















    # {'timestamp': '1525192679', 'franchise': '0053', 'transaction': '12610|173|', 'type': 'AUCTION_WON'}
    # {'timestamp': '1525087225', 'franchise': '0041', 'transaction': '12171|5|', 'type': 'AUCTION_BID'}

    # for bid in bids:





