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

es = Elasticsearch(f"{settings.ES_HOST}:{settings.ES_PORT}")

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


class NewIndex(object):

    def __init__(self):
        super(NewIndex, self).__init__()
        self.step_size = settings.ES_BULK_LIMIT
        self.pp = pprint.PrettyPrinter(indent=2, depth=10)  # pragma: no cover
        self.db_wait = settings.DATABASE_CALLS_WAIT

    def setup(self):
        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)

    def create_index(self):

        one_shard_index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 1
            }
        }

        # properties and conferences are continiously being updated (not "appended" like sessions ..etc), thus their indices
        # have always an "indexing overhead" to be accounted for, for this, we initially give them 02 shards. Even though their
        # index size is very small, this would give enough room for distributing and speeding up queries against conferences and properties.
        two_shards_index_settings = {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1
            }
        }

        # sessions need special handling in terms of shards
        six_shards_index_settings = {
            "settings": {
                "number_of_shards": 6,
                "number_of_replicas": 1
            }
        }

        indices_config = {
            "elevenos": {
                "settings": {
                    "number_of_shards": 24,
                    "number_of_replicas": 1
                }
            },
            "properties": two_shards_index_settings,
            "conferences": two_shards_index_settings,
            "sessions": six_shards_index_settings,
            "accounts": one_shard_index_settings, 
            "devices": one_shard_index_settings,
        }

        # Create `elevenos` index if it does not exist, required for tests

        index_name = 'elevenos'
        try:
            es.indices.get(index=index_name)
        except NotFoundError as err:
            es.indices.create(index='elevenos', body=indices_config["elevenos"])

        # Create the new (static) indices
        new_indices = {
            'properties': {'doc_type': 'property', 'body': property_mapping},
            'conferences': {'doc_type': 'conference', 'body': conference_mapping}
        }

        for index_name, props in new_indices.items():
            try:
                es.indices.create(index=index_name, body=indices_config[index_name])
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
            body.update(indices_config[template_name])
            es.indices.put_template(name=template_name, body=body)
            logger.info(f"Created/Updated {template_name} template")

        doc = {'id': '1'}
        es.index(index='sessions-2018-06', doc_type='sessions', id=1, body=doc)
        es.index(index='devices-2014-01', doc_type='devices', id=1, body=doc)

        create_elevenos_aliases(es, logger)
