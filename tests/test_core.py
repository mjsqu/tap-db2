"""Tests standard tap features using the built-in SDK tests library."""

import datetime
import os

from singer_sdk.testing import get_tap_test_class

from tap_db2.tap import Tapdb2
from tap_db2.client import db2Connector
import sqlalchemy


SAMPLE_CONFIG =  {'hostname': os.environ['TAP_DB2_HOSTNAME'],
                       'username': os.environ['TAP_DB2_USERNAME'],
                       'password': os.environ['TAP_DB2_PASSWORD'],
                       'port': os.environ['TAP_DB2_PORT'],
                       'database': os.environ['TAP_DB2_DATABASE'],
                       }


conn = db2Connector(SAMPLE_CONFIG)
print([stream['tap_stream_id'] for stream in conn.discover_catalog_entries()])


# Run standard built-in tap tests from the SDK:
#TestTapdb2 = get_tap_test_class(
#    tap_class=Tapdb2,
#    config=SAMPLE_CONFIG,
#)


# TODO: Create additional tests as appropriate for your tap.
