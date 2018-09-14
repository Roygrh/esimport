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
from esimport import settings

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

    @staticmethod
    def get_monitoring_metric():
        return settings.DATADOG_SESSION_METRIC


    """
    Loop to continuously find new Sessions and add them to Elasticsearch
    """
    def sync(self, start_date):

        start = self.max_id() + 1

        while True:
            count = 0
            metric_value = None

            logger.debug("Get Sessions from {0} to {1} since {2}"
                .format(start, start+self.db_record_limit, start_date))

            for session in self.model.get_sessions(start, self.db_record_limit, start_date):
                count += 1
                logger.debug("Record found: {0}".format(session.get('ID')))

                _action = super(SessionMapping, self).get_site_values(session.get('ServiceArea'))

                if 'TimeZone' in _action:
                    for pfik, pfiv in self.dates_to_localize:
                        _action[pfiv] = convert_utc_to_local_time(session.record[pfik], _action['TimeZone'])

                session.update(_action)
                metric_value = session.get(self.model.get_key_date_field())

                self.add(session.es(), self.step_size, metric_value)
                start = session.get('ID') + 1

            # for cases when all/remaining items count were less than limit
            self.add(None, 0, metric_value)

            # only wait between DB calls when there is no delay from ES (HTTP requests)
            if count == 0:
                wait = self.db_wait * 2     # noticing the process hanging without error from time to time; might need more sleep between calls
                logger.info("[Delay] Reset SQL connection and waiting {0} seconds".format(wait))
                self.model.conn.reset()
                time.sleep(wait)



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
