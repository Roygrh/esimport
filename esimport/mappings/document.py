import logging



from esimport.mappings.base import BaseMapping
from esimport.mappings.property import PropertyMapping

logger = logging.getLogger(__name__)


class DocumentMapping(BaseMapping):


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

    def setup(self):  # pragma: no cover
        BaseMapping.setup(self)
        # ARRET! possible cycle calls in future
        self.pm = PropertyMapping()
        self.pm.setup()
