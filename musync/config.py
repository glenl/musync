""" Various configuration routines for musync.
"""
import logging
import time
import musync

ARCHIVE_TOP = 'http://www.mutopiaproject.org/ftp'

_MSG_FORMAT='%(asctime)s - %(name)s %(levelname)s - %(message)s'
_DATE_FORMAT='%Y-%m-%d %H:%M:%S'

class UTCFormatter(logging.Formatter):
    converter = time.gmtime

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'utc': {
            '()': UTCFormatter,
            'format': _MSG_FORMAT,
            'datefmt': _DATE_FORMAT,
        },
        'local': {
            'format': _MSG_FORMAT,
            'datefmt': _DATE_FORMAT,
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'utc',
            'level': 'INFO',
        },
        'logfile': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'musync.log',
            'formatter': 'utc',
            'level': 'INFO',
            'backupCount': 3,
            'maxBytes': 2048,
        },
    },
    'root': {
        'handlers': ['console', 'logfile'],
    }
}
