################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import logging

from esimport.mappings.doc import DocumentMapping
from esimport.mappings.property import PropertyMapping

logger = logging.getLogger(__name__)

"""
This class is the base class for any mapping that will append property
data into the documents. 
"""
class PropertyAppendedDocumentMapping(DocumentMapping):
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

    dates_from_pacific = ()
    dates_to_localize = ()

    def __init__(self):
        super(PropertyAppendedDocumentMapping, self).__init__()

    def setup(self):  # pragma: no cover
        DocumentMapping.setup(self)
        # ARRET! possible cycle calls in future
        self.pm = PropertyMapping()
        self.pm.setup()

    """
    Grab the site level org values and information given a organization number
    """
    def get_site_values(self, org_number):
        _action = {}
        for prop in self.pm.get_properties_by_org_number(org_number):
            for pfik, pfiv in self.property_fields_include:
                _action[pfik] = prop.get(pfiv or pfik, "")
            break

        return _action
