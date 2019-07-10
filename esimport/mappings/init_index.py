################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import logging
import pprint

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError, NotFoundError

from constants import PROD_EAST_ENV, PROD_WEST_ENV
from esimport import settings
from esimport.mappings.indices_definitions import conference_mapping
from esimport.mappings.indices_definitions import elevenos_aliases_config
from esimport.mappings.indices_definitions import index_templates
from esimport.mappings.indices_definitions import property_mapping

es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

logger = logging.getLogger(__name__)


def create_elevenos_aliases(es, logger):
    # Create our new aliases that groups dynamic indices together by their index/document type

    for type_, alias in elevenos_aliases_config.items():
        es.indices.update_aliases(body={
            "actions": [
                {
                    "add" : {
                        "index": "elevenos",
                        "alias": alias,
                        "filter": {"type": {"value": type_}}
                    }
                }
            ]
        })
        logger.info(f"Updated {alias} alias to include 'elevenos' index")


class new_index(object):
    es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

    def __init__(self):
        super(new_index, self).__init__()
        self.step_size = settings.ES_BULK_LIMIT
        self.pp = pprint.PrettyPrinter(indent=2, depth=10)  # pragma: no cover
        self.db_wait = settings.DATABASE_CALLS_WAIT

    def setup(self):
        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

    def create_index(self):
        # TODO: fix tests, if index already exist this method will throw exception.
        #  And during tesing this method are being called multiple times

        if settings.ENVIRONMENT in [PROD_WEST_ENV, PROD_EAST_ENV]:
            create_index = {
                "settings": {
                    "number_of_shards": 24,
                    "number_of_replicas": 1
                }
            }
        else:
            create_index = {
                "settings": {
                    "number_of_shards": 9,
                    "number_of_replicas": 1
                }
            }

        # Create `elevenos` index if it not exits, it requires for tests

        index_name = 'elevenos'
        try:
            es.indices.get(index=index_name)
        except NotFoundError as err:
            es.indices.create(index='elevenos', body=create_index)

        # Create the new (static) indices
        new_indices = {
            'properties': {'doc_type': 'property', 'body': property_mapping},
            'conferences': {'doc_type': 'conference', 'body': conference_mapping}
        }

        for index_name, props in new_indices.items():
            try:
                es.indices.create(index=index_name, body=create_index)
                es.indices.refresh(index=index_name)
                es.indices.put_mapping(index=index_name, doc_type=props['doc_type'], body=props['body'])
                logger.info(f"Created {index_name} index")
            except RequestError as e:
                if e.error != 'index_already_exists_exception':
                    raise

                err_msg = str(e)
                logger.warning(f"Failed to create {index_name} index, got {err_msg}")

        # Create index templates for dynamic indices (our date-partitioned indices)

        for template_name, body in index_templates.items():
            body.update(create_index)
            es.indices.put_template(name=template_name, body=body)
            logger.info(f"Created/Updated {template_name} template")

        doc = {'id': '1'}
        es.index(index='sessions-2018-06', doc_type='sessions', id=1, body=doc)
        es.index(index='devices-2014-01', doc_type='devices', id=1, body=doc)

        create_elevenos_aliases(es, logger)

