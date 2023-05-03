import os
import singer
import tap_db2
import tap_db2.sync_strategies.common as common
from tap_db2.connection import get_db2_sql_engine

def display_config():
    print(args)

def get_db_config():
    config = {}
    config["host"] = os.environ.get("TAP_MYSQL_HOST")
    config["port"] = int(os.environ.get("TAP_MYSQL_PORT"))
    config["user"] = os.environ.get("TAP_MYSQL_USER")
    config["password"] = os.environ.get("TAP_MYSQL_PASSWORD")
    config["charset"] = "utf8"
    if not config["password"]:
        del config["password"]

    return config


def get_test_connection():
    """
    Connects to DB2 and returns the connection object
    """
    db_config = get_db_config()

    return mysql_conn


def discover_catalog(connection, catalog):
    catalog = tap_mysql.discover_catalog(connection, catalog)
    streams = []

    for stream in catalog.streams:
        database_name = common.get_database_name(stream)

        if database_name == DB_NAME:
            streams.append(stream)

    catalog.streams = streams

    return catalog


def set_replication_method_and_key(stream, r_method, r_key):
    new_md = singer.metadata.to_map(stream.metadata)
    old_md = new_md.get(())
    if r_method:
        old_md.update({"replication-method": r_method})

    if r_key:
        old_md.update({"replication-key": r_key})

    stream.metadata = singer.metadata.to_list(new_md)
    return stream

def select_stream_from_catalog(catalog_file,tap_stream_id):
    import json
    with open(catalog_file,'r') as f:
        catalog = json.load(f)
    
    streams = catalog.get('streams')
    selected_stream = [stream for stream in streams if stream.get('tap_stream_id') == tap_stream_id]
    new_catalog = {"streams":selected_stream}
    return json.dumps(new_catalog)