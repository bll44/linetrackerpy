from helpers.utils.logger import configure_logging
from helpers.utils.db import *


_logger = configure_logging(__name__, level='DEBUG')


def get_game_data(id=None):
    cursor = get_cursor()
