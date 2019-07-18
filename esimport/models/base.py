################################################################################
# Copyright 2002-2017 Eleven Wireless Inc.  All rights reserved.
#
# This file is the sole property of Eleven Wireless Inc. and can not be used
# or distributed without the expressed written permission of
# Eleven Wireless Inc.
################################################################################

import time
import pyodbc
import logging

from esimport import settings

logger = logging.getLogger(__name__)


class BaseModel(object):
    conn = None

    def __init__(self, connection):
        self.conn = connection

    def execute(self, query, *args):
        # As Eleven uses availability groups, we can't specify db name in DSN string. Rather we have
        # to send an USE command. The API in the pyodbc connector doesn't allow multiple statements
        # in a SQL call. As it remembers context, it's used before every transaction.
        self.conn.cursor.execute("USE Eleven_OS")
        return self.conn.cursor.execute(query, list(args))

    def fetch(self, query, *args, column_names=None):
        for row in self.execute(query, *args):
            if column_names:
                yield dict([(cn, getattr(row, cn, '')) for cn in column_names])
            else:
                yield row

    def fetch_dict(self, query, *args):
        rows = self.execute(query, *args)
        column_names = [column[0] for column in rows.description]
        for row in rows:
            if not isinstance(row, dict):
                yield dict([(cn, getattr(row, cn, '')) for cn in column_names])
            else:
                yield row
