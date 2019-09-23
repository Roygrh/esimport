################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import logging
import time

from esimport import settings
from esimport.mappings.appended_doc import PropertyAppendedDocumentMapping
from esimport.models.conference import Conference
from esimport.utils import convert_utc_to_local_time

logger = logging.getLogger(__name__)


class ConferenceMapping(PropertyAppendedDocumentMapping):
    dates_to_localize = (
        ('DateCreatedUTC', 'DateCreatedLocal'),
        ('StartDateUTC', 'StartDateLocal'),
        ('EndDateUTC', 'EndDateLocal'))

    def __init__(self):
        super(ConferenceMapping, self).__init__()
        self.default_query_limit = 20

    def setup(self):  # pragma: no cover
        super(ConferenceMapping, self).setup()
        self.model = Conference(self.conn)
        self._version_date_fieldname = self.model._version_date_fieldname

    @staticmethod
    def get_monitoring_metric():
        return settings.DATADOG_CONFERENCE_METRIC

    def process_conferences_from_id(self, next_id_to_process: int, start_date) -> (int, int):
        """

        :param next_id_to_process:
        :param start_date: - not the main criterion for querying records, only used to limit  timespan of processing.
        In consequent calls that parameter usually should be the same.
        :return:
        """
        count = 0
        metric_value = None
        for conference in self.model.get_conferences(next_id_to_process, self.default_query_limit,  start_date):
            count += 1
            logger.debug("Record found: {0}".format(conference.get('ID')))

            # get some properties from PropertyMapping
            _action = super(ConferenceMapping, self).get_site_values(conference.get('ServiceArea'))

            if 'TimeZone' in _action:
                for pfik, pfiv in self.dates_to_localize:
                    _action[pfiv] = convert_utc_to_local_time(conference.record[pfik], _action['TimeZone'])

            conference.update(_action)

            metric_value = conference.get(self.model.get_key_date_field())

            self.add(conference.es(), metric_value)
            next_id_to_process = conference.record.get('ID') + 1

        # for cases when all/remaining items count were less than limit
        self.add(None, metric_value)

        return count, next_id_to_process


    """
    Continuously update ElasticSearch to have the latest Conference data
    """
    def update(self, start_date):
        next_id_to_process = 0
        timer_start = time.time()
        while True:
            count, next_id_to_process = self.process_conferences_from_id(
                next_id_to_process=next_id_to_process,
                start_date=start_date
            )

            # always wait between DB calls
            time.sleep(self.db_wait)

            elapsed_time = int(time.time() - timer_start)

            # habitually reset mssql connections.
            if count == 0 or elapsed_time >= self.db_conn_reset_limit:
                wait = self.db_wait * 4
                logger.info("[Delay] Reset SQL connection and waiting {0} seconds".format(wait))
                self.model.conn.reset()
                time.sleep(wait)
                timer_start=time.time() # reset timer
                # start over again when all records have been processed
                if count == 0:
                    next_id_to_process = 0
