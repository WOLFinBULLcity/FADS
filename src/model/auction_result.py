#!/usr/bin/python
# import config
# import line_profiler

# from datetime import datetime
# from datetime import timedelta
# from money import Money

# @profile
# def bid_str(bid):
#   return str(bid.amount.format("en_US", '$#0', False))
#
class Auction_Result:

# {'franchise': '0001',
#  'lastBidTime': '1524441216',
#  'player': '13128',
#  'timeStarted': '1524441202',
#  'winningBid': '67'}

  # @profile
  def __init__(self, dct):
    self.franchise = dct['franchise']
    self.lastBidTime = dct['lastBidTime']
    self.player = dct['player']
    self.timeStarted = dct['timeStarted']
    self.winningBid = dct['winningBid']

  # @profile
  def __str__(self):
    return str(self.__dict__)

  # @profile
  def __eq__(self, other):
    return (
        self.franchise == other.franchise and
        self.lastBidTime == other.lastBidTime and
        self.player == other.player and
        self.timeStarted == other.timeStarted and
        self.winningBid == other.winningBid
    )

  def as_auction_result(self, json_dict):
    return Auction_Result(json_dict)