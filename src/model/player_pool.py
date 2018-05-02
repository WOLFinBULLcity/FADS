# !/usr/local/bin/python
from collections import OrderedDict
from datetime import datetime

import math


class Player_Pool:

  def __init__(self, last_update, players=None, positions=None, years=None):
    print("Initializing player pool...")

    self.last_update = last_update
    self.players = players
    self.positions = positions
    self.years = years

    self.eligible_players = {}

    for p in positions:
      pos_ref = '{}s'.format(p)
      setattr(self, pos_ref, {})

    self.filter_by_position()
    self.alphabetize()

  @staticmethod
  def get_display_name(name):
    return ' '.join(name.split(', ')[::-1])

  def eligible_player_generator(self):
    default = 'N/A'
    for player in self.players:
      position = player.get('position', default)
      draft_year = player.get('draft_year', default)
      if position not in self.positions:
        continue
      if self.years:
        if draft_year not in self.years.keys():
          continue
        if player.get('birthdate'):
          birthday = datetime.fromtimestamp(int(player.get('birthdate')))
          now = datetime.now()
          age = math.floor((now.date() - birthday.date()).days / 365.25)
          player['birthdate_formatted'] = birthday.strftime('%m/%d/%Y')
          player['age'] = age

        player['eligibility'] = self.years[draft_year]
        player['display_name'] = self.get_display_name(player.get('name'))
      yield player

  def filter_by_position(self):
    for player in self.eligible_player_generator():
      # Convert list of dictionaries to dictionary indexed on ID
      player_id = player.pop("id")

      # Add all eligible players to the eligible players list
      self.eligible_players[player_id] = player

      # Then add the player to the appropriate position-specific list
      pos_list_ref = player['position'] + 's'
      pos_list = getattr(self, pos_list_ref)
      pos_list[player_id] = player

  def alphabetize(self):
    sort_on = 'name'

    self.eligible_players = OrderedDict(sorted(
        self.eligible_players.items(),
        key=lambda item: item[1][sort_on]
    ))

    for p in self.positions:
      pos_ref = '{}s'.format(p)
      pos_list = getattr(self, pos_ref)
      pos_list_sorted = OrderedDict(sorted(
          pos_list.items(),
          key=lambda item: item[1][sort_on]
      ))
      setattr(self, pos_ref, pos_list_sorted)

  @staticmethod
  def player_search_generator(target, params, expression):
    default = 'N/A'

    for player_id, player in target.items():
      hits = 0
      for k, v in params.items():
        found_value = player.get(k, default)
        if found_value != v:
          continue
        hits += 1
      if hits == 0:
        continue
      elif expression == 'AND' and hits != len(params):
        continue
      elif expression == 'OR' and hits < 1:
        continue
      yield player_id, player

  def player_search(self, params, target=None, expression='AND'):
    if target is None:
      target = self.eligible_players
    found_players = {}
    for p_id, player in self.player_search_generator(target, params, expression):
      found_players[p_id] = player
    return found_players
