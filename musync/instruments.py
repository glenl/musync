"""Instrument mapping functions
"""
import re
import logging
import psycopg2


_MATCH_INSTRUMENT_Q = """SELECT instrument
  FROM mutopia_instrument WHERE instrument=%s
"""

_MATCH_MAPPED_INSTRUMENT_Q = """SELECT instrument_id
  FROM update_instrumentmap WHERE raw_instrument=%s
"""
def _translate(cursor, instrument):
    if len(instrument) < 3:
        return None

    cursor.execute(_MATCH_INSTRUMENT_Q, (instrument.capitalize(),))
    match = cursor.fetchone()
    if match:
        return match[0]

    cursor.execute(_MATCH_MAPPED_INSTRUMENT_Q, (instrument.lower(),))
    match = cursor.fetchone()
    if match:
        return match[0]

    return None


_PIECES_WO_INSTRUMENTS_Q = """SELECT piece_id,raw_instrument
  FROM mutopia_piece
  WHERE piece_id NOT IN
    (SELECT piece_id FROM mutopia_piece_instruments)
"""
_MAP_INSTRUMENT_X = """INSERT
  INTO mutopia_piece_instruments (piece_id, instrument_id)
  VALUES (%s, %s)
"""
def update(cursor):
    """Update the instrument list for any piece that is missing
    instruments.
    """
    logger = logging.getLogger(__name__)
    pat = re.compile('\W+')
    pieces = []
    cursor.execute(_PIECES_WO_INSTRUMENTS_Q)
    for result in cursor:
        pieces.append(result)

    for piece in pieces:
        mlist = set()
        for instrument in pat.split(piece['raw_instrument']):
            mapped_i = _translate(cursor, instrument.strip())
            if mapped_i:
                mlist.add(mapped_i)

        if len(mlist) == 0:
            logger.warn('No instruments match for piece %s' %
                        piece['piece_id'])
            next

        logger.info('For raw instrument "%s"' % piece['raw_instrument'])
        for instr in mlist:
            logger.info('   %s' % instr)
            cursor.execute(_MAP_INSTRUMENT_X, (piece['piece_id'], instr))
