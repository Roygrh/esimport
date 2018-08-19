################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import time
import logging

from esimport.utils import convert_utc_to_local_time, convert_pacific_to_utc
from esimport.models.conference import Conference
from esimport.mappings.appended_doc import PropertyAppendedDocumentMapping
from esimport import settings

logger = logging.getLogger(__name__)


class ConferenceMapping(PropertyAppendedDocumentMapping):
    dates_to_localize = (
        ('DateCreatedUTC', 'DateCreatedLocal'),
        ('StartDateUTC', 'StartDateLocal'),
        ('EndDateUTC', 'EndDateLocal'))

    def __init__(self):
        super(ConferenceMapping, self).__init__()

    def setup(self):  # pragma: no cover
        super(ConferenceMapping, self).setup(heartbeat_ping=settings.CONFERENCE_MAPPING_PING)
        self.model = Conference(self.conn)

    """
    Find Conference in SQL and add them to ElasticSearch
    """
    def add_conferences(self, start_date):
        count = 0
        start = self.max_id() + 1
        logger.debug("Get Conferences from {0} to {1} since {2}"
              .format(start, start+self.step_size, start_date))
        for conference in self.model.get_conferences(start, self.step_size, start_date):
            count += 1

            _action = super(ConferenceMapping, self).get_site_values(conference.get('ServiceArea'))

            if 'TimeZone' in _action:
                for pfik, pfiv in self.dates_to_localize:
                    _action[pfiv] = convert_utc_to_local_time(conference.record[pfik], _action['TimeZone'])

            conference.update(self.amend_data(conference))
            rec = conference.es()
            logger.debug("Record found: {0}".format(conference.get('ID')))
            self.add(rec, self.step_size)

        # for cases when all/remaining items count were less than limit
        self.add(None, min(len(self._items), self.step_size))

        # only wait between DB calls when there is no delay from ES (HTTP requests)
        if count <= 0:
            self.model.conn.reset()
            logger.debug("[Delay] Waiting {0} seconds".format(self.db_wait))
            time.sleep(self.db_wait)

    """
    Loop to continuously find new Conferences and add them
    """
    def sync(self, start_date):
        while True:
            self.add_conferences(start_date)

    """
    Continuously update ElasticSearch to have the latest Conference data
    """
    def update(self, start_date):
        start = 0
        while True:
            count = 0
            for conference in self.model.get_conferences(start, self.step_size, start_date):
                count += 1
                logger.debug("Record found: {0}".format(conference.get('ID')))

                # get some properties from PropertyMapping
                _action = {}
                _action = super(ConferenceMapping, self).get_site_values(conference.get('ServiceArea'))

                if 'TimeZone' in _action:
                    for pfik, pfiv in self.dates_to_localize:
                        _action[pfiv] = convert_utc_to_local_time(conference.record[pfik], _action['TimeZone'])

                conference.update(_action)
                self.add(dict(conference.es()), self.step_size)
                start = conference.record.get('ID')+1

            # no further conferences with ID >= start
            if count == 0:
                start = 0

            # for cases when all/remaining items count were less than limit
            self.add(None, min(len(self._items), self.step_size))

            # always wait between DB calls
            time.sleep(self.db_wait * 5)
