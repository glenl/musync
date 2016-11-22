"""Setup module for musync.
"""

from setuptools import setup
from os import path

import musync

here = path.abspath(path.dirname(__file__))

setup(
    name = musync.__title__,
    version = musync.__version__,
    description = musync.__summary__,
    url = musync.__uri__,
    author = musync.__author__,
    author_email = musync.__author_email__,
    license = musync.__license__,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Topic :: Database :: Front-Ends',
        'Topic :: Documentation :: Sphinx',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires = [
        'psycopg2>=2.6.2',
        'rdflib>=4.2.1',
    ],
    entry_points={
        'console_scripts': [
            'musync=musync.__main__:main',
        ],
    }
)
