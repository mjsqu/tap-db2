#!/usr/bin/env python3

import backoff

import pyodbc

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

import singer
# import ssl

# from urllib.parse import quote_plus
LOGGER = singer.get_logger()

@backoff.on_exception(backoff.expo, pyodbc.Error, max_tries=5, factor=2)
def connect_with_backoff(connection):
    warnings = []
    with connection.cursor():
        if warnings:
            LOGGER.info(
                (
                    "Encountered non-fatal errors when configuring session "
                    "that could impact performance:"
                )
            )
        for w in warnings:
            LOGGER.warning(w)

    return connection


def decode_sketchy_utf16(raw_bytes):
    """Updates the output handling where malformed unicode is received"""
    s = raw_bytes.decode("utf-16le", "ignore")
    try:
        n = s.index("\u0000")
        s = s[:n]  # respect null terminator
    except ValueError:
        pass
    return s


def modify_ouput_converter(conn):

    prev_converter = conn.connection.get_output_converter(pyodbc.SQL_WVARCHAR)
    conn.connection.add_output_converter(
        pyodbc.SQL_WVARCHAR, decode_sketchy_utf16
    )

    return prev_converter


def revert_ouput_converter(conn, prev_converter):
    conn.connection.add_output_converter(pyodbc.SQL_WVARCHAR, prev_converter)


def get_db2_sql_engine(config) -> Engine:
    """Using parameters from the config to connect to DB2 using ibm_db_sa+pyodbc"""

    # connection_string = "ibm_db_sa+pyodbc://db2inst1:*
    # @localhost:50000/TESTDB"
    connection_string = "ibm_db_sa+pyodbc://{}:{}@{}:{}/{}".format(
        config["username"],
        config["password"],
        config["hostname"],
        config["port"],
        config["database"],
    )
    engine = create_engine(connection_string)

    return engine

def ResultIterator(cursor, arraysize=1):
    while True:
        results = cursor.fetchmany(arraysize)
        if not results:
            break
        for result in results:
            yield result
