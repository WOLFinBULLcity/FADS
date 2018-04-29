class Player_Pool:

  def __init__(self, last_update, players=None, positions=None, years=None):
    print("Initializing player pool...")

    self.last_update = last_update
    self.players = players
    self.positions = positions
    self.years = years

    self.eligible_players = []
    self.QBs = []
    self.RBs = []
    self.WRs = []
    self.TEs = []

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
        player['eligibility'] = self.years[draft_year]
        player['display_name'] = self.get_display_name(player.get('name'))
      yield player

  def filter_by_position(self):
    for player in self.eligible_player_generator():
      # Add all eligible players to the eligible players list
      self.eligible_players.append(player)

      # Then add the player to the appropriate position-specific list
      pos_list_ref = player['position'] + 's'
      pos_list = getattr(self, pos_list_ref)
      pos_list.append(player)

  def alphabetize(self):
    sort_on = 'name'

    self.eligible_players = sorted(
        self.eligible_players,
        key=lambda item: item[sort_on]
    )
    self.QBs = sorted(
        self.QBs,
        key=lambda item: item[sort_on]
    )
    self.RBs = sorted(
        self.RBs,
        key=lambda item: item[sort_on]
    )
    self.WRs = sorted(
        self.WRs,
        key=lambda item: item[sort_on]
    )
    self.TEs = sorted(
        self.TEs,
        key=lambda item: item[sort_on]
    )

  def player_search_generator(self, params, expression):
    default = 'N/A'

    for player in self.eligible_players:
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
      yield player

  def player_search(self, params, expression='AND'):
    found_players = []
    for player in self.player_search_generator(params, expression):
      found_players.append(player)
    return found_players if len(found_players) != 1 else found_players[0]
