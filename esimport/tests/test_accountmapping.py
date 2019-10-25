################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################
from unittest import TestCase

from mock import Mock, MagicMock

from esimport import tests
from esimport.mappings.account import AccountMapping
from esimport.models import ESRecord
from esimport.models.account import Account


class TestAccountMapping(TestCase):
    def setUp(self):
        self.rows = self.multiple_orders = tests._mocked_sql()

        self.am = AccountMapping()
        self.start = 0
        self.end = self.start + min(len(self.rows), self.am.step_size)

        conn = Mock()
        self.am.model = Account(conn)
        self.am.model.conn.cursor = Mock()
        self.am.model.conn.cursor.execute = MagicMock(return_value=self.rows)

    def test_setup_config(self):
        am = AccountMapping()
        assert am.step_size is not None
        assert am.esTimeout is not None
        assert am.esRetry is not None

    # whether returned result count is equal to request count
    def test_get_accounts(self):
        accounts = self.am.model.get_accounts_by_created_date(self.start, self.end)
        account_count = 0
        for account in accounts:
            self.assertIsInstance(account, ESRecord)
            account_count += 1
        self.assertEqual(account_count, len(self.rows))
