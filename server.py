import cherrypy
import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
_logger.addHandler(ch)

class LTServer(object):

    @cherrypy.expose
    def index(self):
        return "index page"