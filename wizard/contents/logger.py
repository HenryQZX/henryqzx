import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

_logDir = Path(__file__).parent.parent.absolute() / 'logs'

if not _logDir.exists():
    _logDir.mkdir(parents=True)

WizardLogger = logging.getLogger("wizard")

_consoleHandler = logging.StreamHandler()
_fileHandler = TimedRotatingFileHandler(
    _logDir / 'wizard_server.log', when='D', backupCount=7
)

_formater = logging.Formatter(
    '%(asctime)s-%(levelname)s-%(funcName)s: %(message)s'
)

_consoleHandler.setFormatter(_formater)
_fileHandler.setFormatter(_formater)

WizardLogger.addHandler(_consoleHandler)
WizardLogger.addHandler(_fileHandler)

WizardLogger.setLevel(logging.INFO)
WizardLogger.setLevel(logging.DEBUG)

log = WizardLogger.info
#log =  print