import logging.handlers
import os

_ZDlog = logging.getLogger('ZD')

_ZDlog.setLevel(logging.DEBUG)

_logPath = os.path.abspath("./logging/ZD.log")

_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

_consoleStreamHandler = logging.StreamHandler()
_consoleStreamHandler.setLevel(logging.DEBUG)
_consoleStreamHandler.setFormatter(_formatter)

_symLogRotFileHandler = logging.handlers.RotatingFileHandler(_logPath, maxBytes=2000000, backupCount=5)
_symLogRotFileHandler.setLevel(logging.DEBUG)
_symLogRotFileHandler.setFormatter(_formatter)

_ZDlog.addHandler(_consoleStreamHandler)
_ZDlog.addHandler(_symLogRotFileHandler)


def LogAJIRMessage(message):
    _ZDlog.info(message)


def LogZDError(message):
    _ZDlog.error(message)
