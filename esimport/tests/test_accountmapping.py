from unittest import TestCase

import testing.elasticsearch

from esimport.mappings.account import AccountMapping


class TestAccountMapping(TestCase):

    def setUp(self):
        self.am = AccountMapping()

    def test_setup_config(self):
        assert self.am.cfg is None
        assert self.am.step_size is None
        assert self.am.position is None
        assert self.am.esTimeout is None
        assert self.am.esRetry is None

        self.am.setup_config()

        assert self.am.cfg is not None
        assert self.am.step_size is not None
        assert self.am.position is not None
        assert self.am.esTimeout is not None
        assert self.am.esRetry is not None
