"""musync module
"""
import logging

__all__ = (
    '__title__', '__summary__', '__version__',
    '__author__', '__license__', '__copyright__',
    '__author_email__', '__uri__'
)

__title__ = 'musync'
__summary__ = 'Synchronize published sheet music with site database'
__version__ = '0.0.1'

__author__ = 'Glen Larsen'
__author_email__= 'glenl.glx@gmail.com'
__uri__ = 'http://mutopiaproject.org/'

__license__ = 'MIT'
__copyright__ = 'Copyright 2016 The Mutopia Project'

from .exceptions import BadConfiguration
from .dbutils import get_connection, publish
from .utils import parse_mutopia_id
from .instruments import update
from .config import LOGGING, ARCHIVE_TOP
