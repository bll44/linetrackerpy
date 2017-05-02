import os

# region Scoresandodds API config
# base json api url for scoresandodds
feed_url = "http://www.scoresandodds.com/feeds/day/"
# endregion

# region Database config
db_file_name = "linetracker.db"
db_file = os.path.abspath(os.path.join(__file__, "..", "..", "database", db_file_name))
# endregion

# region SQL queries
query = {'day': {}}
query['day']['insert'] = """
INSERT INTO day (day_id, date, lastmodified) VALUES (?, ?, ?)
"""
query['day']['check_day_exists'] = """
SELECT * FROM day WHERE date = ?
"""
query['day']['update_lastmodified'] = """
UPDATE day SET lastmodified = ? WHERE date = ?
"""
# endregion

# region League config
selected_leagues = ['NBA', 'MLB', 'NHL']
# endregion