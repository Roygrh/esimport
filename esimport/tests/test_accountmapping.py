from unittest import TestCase

import testing.elasticsearch

from esimport.mappings.account import AccountMapping


class TestAccountMapping(TestCase):

    def setUp(self):
        self.am = AccountMapping()

    def test_setup_config(self):
        am = AccountMapping()

        assert am.cfg is None
        assert am.step_size is None
        assert am.position is None
        assert am.esTimeout is None
        assert am.esRetry is None

        am.setup_config()

        assert am.cfg is not None
        assert am.step_size is not None
        assert am.position is not None
        assert am.esTimeout is not None
        assert am.esRetry is not None

        am.setup_config()
