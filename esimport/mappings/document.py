import six
import time
import pprint
import logging

from elasticsearch import Elasticsearch
from elasticsearch import exceptions

from esimport import settings
from esimport.utils import retry
from esimport.utils import convert_utc_to_local_time
from esimport.models import ESRecord
from esimport.models.account import Account
from esimport.connectors.mssql import MsSQLConnector
from esimport.mappings.base import BaseMapping
from esimport.mappings.property import PropertyMapping

logger = logging.getLogger(__name__)


class DocumentMapping(BaseMapping):
    step_size = None
    esTimeout = None
    esRetry = None

    model = None
    es = None

    pm = None
    property_fields_include = (
        ('PropertyName', 'Name'),
        ('PropertyNumber', 'Number'),
        ('Provider', None),
        ('Brand', None),
        ('MARSHA_Code', None),
        ('Country', None),
        ('Region', None),
        ('SubRegion', None),
        ('OwnershipGroup', None),
        ('TaxRate', None),
        ('CorporateBrand', None),
        ('ExtPropId', None),
        ('TimeZone', None))

    def __init__(self):
        super(DocumentMapping, self).__init__()
        self.pp = pprint.PrettyPrinter(indent=2, depth=10)  # pragma: no cover
        self.step_size = settings.ES_BULK_LIMIT
        self.esTimeout = settings.ES_TIMEOUT
        self.esRetry = settings.ES_RETRIES
        self.db_wait = settings.DATABASE_CALLS_WAIT

    def setup(self):  # pragma: no cover
        logger.debug("Setting up DB connection")
        conn = MsSQLConnector()

        # ARRET! possible cycle calls in future
        self.pm = PropertyMapping()
        self.pm.setup()

        logger.debug("Setting up ES connection")
        # defaults to localhost:9200
        self.es = Elasticsearch(settings.ES_HOST + ":" + settings.ES_PORT)
