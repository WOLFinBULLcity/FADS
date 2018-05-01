# !/usr/local/bin/python


class League_Data:

  def __init__(
      self,
      last_update,
      conferences=None,
      divisions=None,
      franchises=None
  ):
    print("Initializing league data...")

    self.last_update = last_update

    # Convert lists of dictionaries to dictionaries indexed on ID
    self.conferences = {c.pop("id"): c for c in conferences}
    self.divisions = {d.pop("id"): d for d in divisions}
    self.franchises = {f.pop("id"): f for f in franchises}

  @staticmethod
  def league_search_generator(target, params, expression):
    default = 'N/A'

    for t in target:
      hits = 0
      for k, v in params.items():
        found_value = t.get(k, default)
        if found_value != v:
          continue
        hits += 1
      if hits == 0:
        continue
      elif expression == 'AND' and hits != len(params):
        continue
      elif expression == 'OR' and hits < 1:
        continue
      yield t

  def league_search(self, params, target=None, expression='AND'):
    if target is None:
      target = self.franchises

    results = []
    for r in self.league_search_generator(target, params, expression):
      results.append(r)
    return results if len(results) != 1 else results[0]

  def conference_id_from_franchise_id(self, franchise_id: str):
    id = self.divisions[self.franchises[franchise_id]["division"]]["conference"]
    return id


