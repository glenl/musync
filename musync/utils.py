"""Miscellaneous utility functions.
"""
from datetime import date
import re

_MUID_PATTERN = re.compile('Mutopia-([0-9]{4})/(\d\d?)/(\d\d?)-([0-9]*)$')

def parse_mutopia_id(mutopia_id):
    """Parse a Mutopia mutopia_id string, typically from an RDF file, and
    return a tuple containing the publication date and piece-id.

    For example::

        Mutopia-2016/20/12-33 ==> ("2016/20/12", "33")
        Mutopia-2016/20/12-AB ==> None

    :param str mutopia_id: The mutopia mutopia_id string, expected to be in
        the appropriate format.
    :return: A tuple containing a (datetime.date, id)

    """
    if mutopia_id:
        fmat = _MUID_PATTERN.search(mutopia_id)
        if fmat:
            try:
                pub_date = date(int(fmat.group(1)),
                                int(fmat.group(2)),
                                int(fmat.group(3)))
                return (pub_date, fmat.group(4))
            except TypeError:
                raise ValueError('Invalid date on input from %s' % fmat.group(0))

    raise ValueError('Empty or mal-formed mutopia id')
