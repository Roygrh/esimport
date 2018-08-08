################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import time
import logging

from esimport.utils import convert_utc_to_local_time
from esimport.models.session import Session
from esimport.mappings.appended_doc import PropertyAppendedDocumentMapping

logger = logging.getLogger(__name__)


class SessionMapping(PropertyAppendedDocumentMapping):
    dates_to_localize = (
        ('LoginTime', 'LoginTimeLocal'),
        ('LogoutTime', 'LogoutTimeLocal'))

    def __init__(self):
        super(SessionMapping, self).__init__()

    def setup(self):  # pragma: no cover
        super(SessionMapping, self).setup()
        self.model = Session(self.conn)

    """
    Find Sessions in SQL and add them to ElasticSearch
    """
    def add_sessions(self, start_date, limit):
        count = 0        
        start = self.max_id() + 1
        logger.debug("Get Sessions from {0} to {1} since {2}"
              .format(start, start+limit, start_date))
        for session in self.model.get_sessions(start, limit, start_date):
            count += 1

            _action = super(SessionMapping, self).get_site_values(session.get('ServiceArea'))

            if 'TimeZone' in _action:
                for pfik, pfiv in self.dates_to_localize:
                    _action[pfiv] = convert_utc_to_local_time(session.record[pfik], _action['TimeZone'])

            session.update(_action)

            rec = session.es()
            logger.debug("Record found: {0}".format(session.get('ID')))
            self.add(rec, self.step_size)

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))

        # only wait between DB calls when there is no delay from ES (HTTP requests)
        if count <= 0:
            self.model.conn.reset()
            logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
            time.sleep(self.db_wait)

        return count

    """
    Loop to continuously find new Sessions and add them
    """
    def sync(self, start_date):
        limit = self.db_record_limit

        while True:
            count = self.add_sessions(start_date, limit)

            if count > 0:
                limit = self.db_record_limit
            else:
                limit *= 2  # increase limit if no sessions were processed


    """
    NON FUNCTIONAL. Needs to be implemented.
    """
    def backload(self, start_date):
        start = 0
        for session in self.model.get_sessions(start, self.step_size, start_date):
            rec = session.es()
            logger.debug("Record found: {0}".format(self.pp.pformat(rec)))
            self.add(dict(rec), self.step_size)
            start = session.get('ID') + 1

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))
