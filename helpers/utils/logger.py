import logging


_valid_logging_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
_logger = None

# Configures and returns a logger for the file in which it is called
def configure_logging(name, level='INFO', format=False):
    _logger = logging.getLogger(name)
    # Ensure a valid logging level has been passed in
    if level.upper() not in _valid_logging_levels:
        _logger.setLevel(logging.DEBUG)
        _logger.debug('Logging level "%s" is not a valid logging level' % level)
    else:
        _logger.info('Setting logging level to %s for %s' % (level, name))
        _logger.setLevel(getattr(logging, level.upper()))

    # region StreamHandler configuration
    ch = logging.StreamHandler()
    if format:
        ch.setFormatter(logging.Formatter(format))
    else:
        ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s> %(message)s'))

    # add the console stream handler to the _logger
    _logger.addHandler(ch)
    # endregion

    return _logger