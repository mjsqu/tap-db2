"""db2 tap class."""

from __future__ import annotations

from singer_sdk import SQLTap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_db2.client import db2Stream


class Tapdb2(SQLTap):
    """db2 tap class."""

    name = "tap-db2"
    default_stream_class = db2Stream

    config_jsonschema = th.PropertiesList(
        th.Property(
            "hostname",
            th.StringType,
            required=True,
            description="The hostname or IP address",
        ),
        th.Property(
            "password",
            th.StringType,
            secret=True,
            required=True,
            description="Password",
        ),
        th.Property(
            "username",
            th.StringType,
            secret=True,
            required=True,
            description="Username to connect with",
        ),
        th.Property(
            "port",
            th.StringType,
            default="50000",
            description="The port number",
        ),
        th.Property(
            "database",
            th.StringType,
            default="sample",
            description="The name of the database on the host",
        ),
    ).to_dict()


if __name__ == "__main__":
    Tapdb2.cli()
