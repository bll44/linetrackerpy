import cherrypy
import logging
from lib.logger import configure_logging
import sqlite3
from lib import db
from pprint import pprint


_logger = configure_logging(__name__, level='DEBUG')

class LTServer(object):

    @cherrypy.expose
    def index(self):
        _logger.info('testing the configure_logging method')
        return 'Linetrackerpy'

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def view_data(self):
        cursor = db.get_cursor()
        data = cursor.execute('SELECT DISTINCT * FROM games')
        games = []
        for row in data:
            games.append(row)
        db.closedb()
        return games