################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
from unittest import TestCase

from six.moves import range
from mock import MagicMock

from esimport.mappings.property import PropertyMapping


class TestPropertyMapping(TestCase):


    def setUp(self):
        pass


    def test_add(self):
        pm1 = PropertyMapping()
        pm1.bulk_add_or_update = MagicMock()
        for i in range(0):
            pm1.add(dict(ii=i), 500)
        self.assertFalse(pm1.bulk_add_or_update.called)

        pm2 = PropertyMapping()
        pm2.bulk_add_or_update = MagicMock()
        for i in range(499):
            pm2.add(dict(ii=i), 500)
        self.assertFalse(pm2.bulk_add_or_update.called)

        pm3 = PropertyMapping()
        pm3.bulk_add_or_update = MagicMock()
        for i in range(500):
            pm3.add(dict(ii=i), 500)
        self.assertTrue(pm3.bulk_add_or_update.called)

        pm4 = PropertyMapping()
        pm4.bulk_add_or_update = MagicMock()
        for i in range(9):
            pm4.add(dict(ii=i), 10)
        self.assertFalse(pm4.bulk_add_or_update.called)

        pm5 = PropertyMapping()
        pm5.bulk_add_or_update = MagicMock()
        for i in range(10):
            pm5.add(dict(ii=i), 10)
        self.assertTrue(pm5.bulk_add_or_update.called)

        pm6 = PropertyMapping()
        pm6.bulk_add_or_update = MagicMock()
        for i in range(10):
            pm6.add(None, 10)
        self.assertFalse(pm6.bulk_add_or_update.called)


# REVIEW: Please add some tests to test the new ServiceArea functionality.