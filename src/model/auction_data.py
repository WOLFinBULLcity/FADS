# !/usr/local/bin/python

from decimal import *
from model.league_data import League_Data

import itertools


class Auction_Data:

  def __init__(self, ld: League_Data, transactions: list):
    self.ld: League_Data = ld
    self.transactions: list = transactions
    self.conference_auctions = {c: {} for c in ld.conferences}

    self.chronological_order()

    for t in self.transactions:
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
          # First make sure we have a properly completed auction
          r = self.conference_auctions[c_id][p_id]
          i = len(r) - 1
          if r[i]['status'] != 'closed':
            """We've started a new auction without the previous one closing. """
            """Something went wrong, remove the previous auction data."""
            del r[i]

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
        p_auction[idx]['winner'] = t['franchise']

  def conference_totals(self):
    c_totals = {c: {'spent': 0, 'count': 0} for c in self.ld.conferences}
    for c, pa in self.conference_auctions.items():
      for p, a in pa.items():
        for s in a:
          c_totals[c]['spent'] += int(s.get('top_bid'))
          c_totals[c]['count'] += 1

    for c_id, info in c_totals.items():
      funds = 16000 if self.ld.conferences[c_id]['name'] == 'Mid 16' else 14000
      spots = 320 if self.ld.conferences[c_id]['name'] == 'Mid 16' else 280
      spent = info['spent']
      getcontext().prec = 4
      allocation = Decimal(spent) / Decimal(funds) * 100
      roster_pct = Decimal(info['count']) / Decimal(spots) * 100

      print('{}; Auctions: {}; Spent: ${}/${} ({}%); Rosters {}% Full'.format(
            self.ld.conferences[c_id]['name'],
            info['count'],
            spent,
            funds,
            allocation,
            roster_pct
      ))

  def auctions_for_franchise_generator(self, franchise_id):
    c = self.ld.conference_id_from_franchise_id(franchise_id)
    pa = self.conference_auctions[c]
    for p, a in pa.items():
      for s in a:
        if s.get('status') != 'closed' or s.get('winner') != franchise_id:
          continue
        yield p, s

  def auctions_for_franchise(self, franchise_id=None):
    roster_data = {}
    for p, a in self.auctions_for_franchise_generator(franchise_id):
      roster_data[p] = a
    return roster_data

  def auctions_for_player_name(self, player_pool=None, player_name=None):
    p = player_pool.player_search(params={'display_name': player_name})
    player_id = next(iter(p))
    for c_id, c in self.ld.conferences.items():
      auctions = self.auctions_for_player(
          conference_id=c_id,
          player_id=player_id
      )
      if auctions is None:
        continue
      for a in auctions:
        print('{}: Player: {}; Auction: {}; Top Bid: ${}'.format(
            c.get('name'),
            player_pool.eligible_players[player_id].get('display_name'),
            a.get('status'),
            a.get('top_bid')
        ))

  def auctions_for_player(self, conference_id=None, player_id=None):
    if player_id not in self.conference_auctions[conference_id]:
      return None
    return self.conference_auctions[conference_id][player_id]

  def average_price_for_player(self, player_id=None):
    auction_count = 0
    auction_sum = 0

    for c, pa in self.conference_auctions.items():
      for p, a in pa.items():
        if p != player_id:
          continue
        for s in a:
          if s.get('status') == 'closed':
            auction_count += 1
            auction_sum += int(s.get('top_bid'))

    if auction_count == 0:
      return None

    getcontext().prec = 5
    return Decimal(auction_sum) / Decimal(auction_count)

  def chronological_order(self):
    sort_on = 'timestamp'

    self.transactions = sorted(
        self.transactions,
        key=lambda item: item[sort_on]
    )
