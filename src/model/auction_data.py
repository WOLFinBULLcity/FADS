# !/usr/local/bin/python

from model.league_data import League_Data

import itertools


class Auction_Data:

  def __init__(self, ld: League_Data, transactions: dict):
    self.ld: League_Data = ld
    self.transactions: dict = transactions

    self.conference_auctions = {}

    for t in transactions:
      # Get the conference for this transaction
      conference_id = self.ld.conference_id_from_franchise_id(t['franchise'])

      transaction = t.pop('transaction')
      player_id, raw_amount, discard = transaction.split('|')
      t['amount'] = ''.join(itertools.takewhile(str.isdigit, raw_amount))






    # {'timestamp': '1525192679', 'franchise': '0053', 'transaction': '12610|173|', 'type': 'AUCTION_WON'}
    # {'timestamp': '1525087225', 'franchise': '0041', 'transaction': '12171|5|', 'type': 'AUCTION_BID'}

    # for bid in bids:





