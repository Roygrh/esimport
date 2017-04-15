import six

import logging
logger = logging.getLogger(__name__)


def _u(v):
    if isinstance(v, six.string_types):
        if six.PY2 and isinstance(v, unicode):
            return v
        return six.u(v)
    else:
        return v


def convert_keys_to_string(dictionary):
    if not isinstance(dictionary, dict):
        return _u(dictionary)
    return dict((_u(k), convert_keys_to_string(v))
        for k, v in dictionary.items())
