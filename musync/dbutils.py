"""Database functions.
"""

import logging
import os
import psycopg2
from psycopg2.extras import DictCursor
from urllib.error import HTTPError

from rdflib import Graph, URIRef, Namespace, URIRef
from rdflib.term import Literal

import musync


# The RDF namespace definition for retrieving values from an RDF graph.
MP = Namespace('http://www.mutopiaproject.org/piece-data/0.1/')

# The order of this list is the column order of the table definition.
_ORDERED_COLUMNS = [
    'piece_id', 'title', 'raw_instrument',
    'opus', 'lyricist', 'date_composed',
    'date_published', 'source', 'moreinfo',
    'composer_id', 'license_id', 'maintainer_id',
    'style_id', 'version_id',
]


def get_connection():
    if 'RDS_DB_NAME' not in os.environ:
        raise musync.BadConfiguration('Database environment is not set')

    conn = psycopg2.connect(database=os.getenv('RDS_DB_NAME'),
                            user=os.getenv('RDS_USER'),
                            port=os.getenv('RDS_PORT'),
                            host=os.getenv('RDS_HOSTNAME'),
                            password=os.getenv('RDS_PASSWORD'),
                            )
    return conn


_LICENSE_Q = 'SELECT id FROM mutopia_license WHERE name=%s'
def get_license(connection, license_name):
    with connection.cursor() as cursor:
        cursor.execute(_LICENSE_Q, (license_name,))
        license_ref = cursor.fetchone()
        if license_ref:
            return license_ref[0]
    return None


_VERSION_Q = 'SELECT id FROM mutopia_lpversion WHERE version=%s'
_CREATE_VERSION_X = """INSERT
  INTO mutopia_lpversion (id, version, major, minor, edit)
  VALUES (%s, %s, %s, %s, %s)
"""
_MAX_VERSION_ROWID = 'select max(id) from mutopia_lpversion'
def get_version(connection, version):
    with connection.cursor() as cursor:
        cursor.execute(_VERSION_Q, (version,))
        version_ref = cursor.fetchone()
        if version_ref:
            return version_ref[0]
        # insert this version
        cursor.execute(_MAX_VERSION_ROWID)
        rowid = cursor.fetchone()
        if rowid:
            # build the values for insertion
            values = [rowid[0] + 1]
            values.append(version)
            cursor.execute(_CREATE_VERSION_X,
                           values + version.split('.', 2))
            return rowid[0]
    return 0


_PIECE_EXISTS_Q = 'SELECT count(piece_id) FROM mutopia_piece WHERE piece_id=%s'
def piece_exists(connection, piece_id):
    with connection.cursor() as cursor:
        cursor.execute(_PIECE_EXISTS_Q, (piece_id,))
        results = cursor.fetchone()
        if results:
            return results[0] == 1
    return False


_FIND_MAINTAINER_Q = 'SELECT id FROM mutopia_contributor WHERE name=%s'
_MAX_MAINTAINER_ROWID = 'SELECT max(id) FROM mutopia_contributor'
_CREATE_MAINTAINER_X = """INSERT
INTO mutopia_contributor (id,name,email,url) VALUES (%s, %s, %s, %s)
"""
def get_contributor(connection, maintainer, email, url):
    logger = logging.getLogger(__name__)
    logger.info('Looking for %s' % maintainer)
    with connection.cursor() as cursor:
        cursor.execute(_FIND_MAINTAINER_Q, (maintainer,))
        contributor_id = cursor.fetchone()
        if contributor_id:
            logger.info(' found as id %s' % contributor_id[0])
            return contributor_id[0]
        else:
            cursor.execute(_MAX_MAINTAINER_ROWID)
            rowid = cursor.fetchone()
            if rowid:
                next_rowid = rowid[0] + 1
                cursor.execute(_CREATE_MAINTAINER_X,
                               (next_rowid, maintainer, email, url,))
                logging.info('Added contributor with id %s' % next_rowid)
                return next_rowid
            logger.info('failed to add %s' % maintainer)
            return 0

    logger.info('Not found!')
    return 0


def _equals_literally(left, right):
    if isinstance(left, Literal):
        return left.eq(right)
    else:
        return left == right


_PIECE_Q = 'SELECT * FROM mutopia_piece WHERE piece_id=%s'
_PIECE_UPDATE = "UPDATE mutopia_piece SET {0}=%s WHERE piece_id=%s"
def _update(connection, column_dict):
    logger = logging.getLogger(__name__)
    piece = (column_dict['piece_id'],)
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(_PIECE_Q, piece)
        result = cursor.fetchone()
        if not result:
            logger.warn('  No result for piece %s' % column_dict['piece_id'])
            return

        for column in _ORDERED_COLUMNS[1:]:
            if not _equals_literally(column_dict[column], result[column]):
                logger.info('  %s -> %s' % (result[column],
                                            column_dict[column],))
                cursor.execute(_PIECE_UPDATE.format(column),
                               (column_dict[column], piece))


_INSERT_PIECE_X = """INSERT INTO mutopia_piece
(piece_id, title, raw_instrument, opus, lyricist,
 date_composed, date_published, source, moreinfo,
 composer_id, license_id, maintainer_id, style_id, version_id)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
def _process(connection, result):
    logger = logging.getLogger(__name__)
    rdfpath = os.path.join(musync.ARCHIVE_TOP,
                           result['folder'],
                           result['name'] + '.rdf')
    logger.info('reading %s ' % rdfpath)
    graph = Graph().parse(URIRef(rdfpath))

    # Because our RDF's are defined as 'rdf:about:"."' the subject
    # is an URI reference to the containing folder.
    subject = URIRef('/'.join([musync.ARCHIVE_TOP,
                               result['folder'],]) + '/')

    # A footer isn't stored in the database but its bit parts are.
    (pubdate, piece_id) = musync.parse_mutopia_id(graph.value(subject, MP.id))

    column_dict = dict()
    column_dict['piece_id'] = piece_id
    # order is important here: must match db columns!
    column_dict['title'] = graph.value(subject, MP.title)
    column_dict['raw_instrument'] = graph.value(subject, MP['for'])
    column_dict['opus'] = graph.value(subject, MP.opus)
    column_dict['lyricist'] = graph.value(subject, MP.lyricist)
    column_dict['date_composed'] = graph.value(subject, MP.date)
    column_dict['date_published'] = pubdate
    column_dict['source'] = graph.value(subject, MP.source)
    column_dict['moreinfo'] = graph.value(subject, MP.moreinfo)
    column_dict['composer_id'] = graph.value(subject, MP.composer)
    column_dict['license_id'] = get_license(
        connection, graph.value(subject, MP.licence))
    column_dict['maintainer_id'] = get_contributor(
        connection,
        graph.value(subject, MP.maintainer),
        graph.value(subject, MP.maintainerEmail),
        graph.value(subject, MP.maintainerWeb))
    column_dict['style_id'] = graph.value(subject, MP.style)
    column_dict['version_id'] = get_version(
        connection, graph.value(subject, MP.lilypondVersion))

    for key, value in column_dict.items():
        if value is None:
            column_dict[key] = ''

    if column_dict['maintainer_id'] == 0:
        print('maintainer get failed for %s'
              % graph.value(subject, MP.maintainer))
        return 0

    if piece_exists(connection, piece_id):
        logger.info('Beginning UPDATE for piece %s' % piece_id)
        _update(connection, column_dict)
    else:
        logger.info('Beginning INSERT for piece %s' % piece_id)
        with connection.cursor() as cursor:
            values = []
            for column in _ORDERED_COLUMNS:
                values.append(column_dict[column])
            cursor.execute(_INSERT_PIECE_X, values)

    return piece_id


_UNPUBLISHED_Q = """
SELECT id,folder,name,has_lys,piece_id FROM mutopia_assetmap
  WHERE
    piece_id IS NULL
"""
_PUBLISHED_X = 'UPDATE mutopia_assetmap SET piece_id=%s WHERE id=%s'
def publish(args):
    logger = logging.getLogger(__name__)
    limit = ''
    if args.limit > 0:
        limit = ' limit {0}'.format(args.limit)

    published = []
    rejects = []
    with get_connection() as connection:
        with connection.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(_UNPUBLISHED_Q + limit)
            for result in cursor.fetchall():
                try:
                    piece_id = _process(connection, result)
                    if piece_id == 0:
                        print('debugging... skipping %s' % result['id'])
                    else:
                        published.append((piece_id, result['id']))
                except (FileNotFoundError, HTTPError) as exc:
                    print('skipping due to %s' % exc)
                    rejects.append(result['id'])
            for pubs in published:
                cursor.execute(_PUBLISHED_X, pubs)
            # process rejects
            for reject in rejects:
                logger.info('Rejecting update with id %s' % reject)

            musync.instruments.update(cursor)

            # finally, refresh the materialized view
            logger.info('Refreshing materialized view for FTS')
            cursor.execute('REFRESH MATERIALIZED VIEW mutopia_search_view')
