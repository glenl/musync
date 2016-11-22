"""
The main console script entry point.

"""

import argparse
import logging.config
import os
import sys
import musync

def main():
    parser = argparse.ArgumentParser(prog='musync')
    parser.add_argument(
        '--limit',
        type=int,
        default=0,
        help='Limit processing to this number of results'
    )
    args = parser.parse_args(sys.argv[1:])

    logging.config.dictConfig(musync.LOGGING)

    musync.publish(args)


if __name__ == "__main__":
    sys.exit(main())
