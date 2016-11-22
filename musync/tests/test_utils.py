"""Tests for musync.utils module
"""

import os.path
from unittest import TestCase
import musync

class TestUtils(TestCase):
    """utils testing"""

    def test_mutopia_id_parsing(self):
        """mutopia id parsing tests"""

        # empty mutopia_id
        with self.assertRaises(ValueError):
            mu_tuple = musync.parse_mutopia_id(None)

        # badly formed id
        with self.assertRaises(ValueError):
            mu_tuple = musync.parse_mutopia_id('Muto-10/11/12-99')

        # badly formed date
        with self.assertRaises(ValueError):
            musync.parse_mutopia_id('Mutopia-2016/13/1-999')

        # badly formed identifier
        with self.assertRaises(ValueError):
            musync.parse_mutopia_id('Mutopia-2016/11/8-DJT')

        # finally, some good (and big!) id's
        musync.parse_mutopia_id('Mutopia-2016/11/9-1')
        musync.parse_mutopia_id('Mutopia-2016/11/10-999999')
