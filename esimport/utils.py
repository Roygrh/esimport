import six

import logging
logger = logging.getLogger(__name__)


def convert_keys_to_string(dictionary):
    if not isinstance(dictionary, dict):
        if isinstance(dictionary, six.string_types):
            return six.u(dictionary)
        else:
            return dictionary
    return dict((six.u(k), convert_keys_to_string(v))
        for k, v in dictionary.items())
