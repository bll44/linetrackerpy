import os

# region Scoresandodds API config
# base json api url for scoresandodds
feed_url = 'http://www.scoresandodds.com/feeds/day/'
# endregion

# region Database config
db_path = os.path.abspath(os.path.join(__file__, '..', '..', 'database'))
db_name = 'linetracker.db'
db_file = os.path.abspath(os.path.join(db_path, db_name))
# endregion

# region SQL queries

# region Table create statements
# sql for creating the `day` table
create_day_table_sql = """
CREATE TABLE "day" ( `day_id` TEXT NOT NULL, `date` TEXT NOT NULL, 
`lastmodified` INTEGER NOT NULL, PRIMARY KEY(`day_id`) )
"""

# sql for creating the `game` table
create_games_table_sql = """
CREATE TABLE "games" ( `id` TEXT NOT NULL, `day_id` TEXT NOT NULL, `league` TEXT NOT NULL, `game_id` TEXT NOT NULL, 
`date` TEXT NOT NULL, `status` TEXT, `period` TEXT, `away_team` TEXT, `away_sfid` TEXT, `away_openline` TEXT, 
`away_linemovement` TEXT, `away_halftime_currentline` TEXT, `away_currentline` TEXT, `away_currentmoneyline` TEXT, 
`away_pitchername` TEXT, `away_currentrunline` TEXT, `away_moneybettingtrends` TEXT, 
`away_pointspreadbettingtrends` TEXT, `away_totalbettingtrends` TEXT, `home_team` TEXT, `home_sfid` TEXT, 
`home_openline` TEXT, `home_linemovement` TEXT, `home_halftime_currentline` TEXT, `home_currentline` TEXT, 
`home_currentmoneyline` TEXT, `home_pitchername` TEXT, `home_currentrunline` TEXT, `home_moneybettingtrends` TEXT, 
`home_pointspreadbettingtrends` TEXT, `home_totalbettingtrends` TEXT, `created_at` TEXT, PRIMARY KEY(`id`) )
"""

dbtable_create_statements = {
    'day': create_day_table_sql,
    'games': create_games_table_sql
}

verify_table_sql = """
SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?
"""
# endregion
query = {}

# region `day` table queries
query['day'] = {
    'insert': """
    INSERT INTO day (day_id, date, lastmodified) VALUES (?, ?, ?)    
    """,
    'check_day_exists': """
    SELECT * FROM day WHERE date = ?
    """,
    'update_lastmodified': """
    UPDATE day SET lastmodified = ? WHERE date = ?
    """,
    'get_day_id': """
    SELECT day_id FROM day WHERE date = ?
    """
}
# endregion

# region `games` table queries
query['games'] = {
    'insert': """
    INSERT INTO games (
        id,
        day_id,
        league,
        game_id,
        date,
        status,
        period,
        away_team,
        away_sfid,
        away_openline,
        away_linemovement,
        away_halftime_currentline,
        away_currentline,
        away_currentmoneyline,
        away_pitchername,
        away_currentrunline,
        away_moneybettingtrends,
        away_pointspreadbettingtrends,
        away_totalbettingtrends,
        home_team,
        home_sfid,
        home_openline,
        home_linemovement,
        home_halftime_currentline,
        home_currentline,
        home_currentmoneyline,
        home_pitchername,
        home_currentrunline,
        home_moneybettingtrends,
        home_pointspreadbettingtrends,
        home_totalbettingtrends,
        created_at
    ) VALUES (
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?, ?, ?, ?, ?,
        ?, ?
    )
    """
}
# endregion

# query['day']['insert'] = """
# INSERT INTO day (day_id, date, lastmodified) VALUES (?, ?, ?)
# """
# query['day']['check_day_exists'] = """
# SELECT * FROM day WHERE date = ?
# """
# query['day']['update_lastmodified'] = """
# UPDATE day SET lastmodified = ? WHERE date = ?
# """
# endregion

# region League config
selected_leagues = ['NBA', 'MLB', 'NHL']
# endregion