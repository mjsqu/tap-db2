"""SQL client handling.

This includes db2Stream and db2Connector.
"""

from __future__ import annotations

from typing import Any, Iterable

import sqlalchemy  # noqa: TCH002
from sqlalchemy import bindparam

import singer_sdk._singerlib as singer
from singer_sdk import SQLConnector, SQLStream
from singer_sdk.helpers._catalog import pop_deselected_record_properties
from singer_sdk.helpers._util import utc_now



class db2Connector(SQLConnector):
    """Connects to the db2 SQL source."""

    def discover_catalog_entries(self) -> list[dict]:
        """Return a list of catalog entries from discovery.

        Returns:
            The discovered catalog entries as a list.
        """
        result: list[dict] = []
        engine = self._engine
        inspected = sqlalchemy.inspect(engine)
        for schema_name in self.get_schema_names(engine, inspected):
            # Iterate through each table and view
            for table_name, is_view in self.get_object_names(
                engine,
                inspected,
                schema_name,
            ):
                catalog_entry = self.discover_catalog_entry(
                    engine,
                    inspected,
                    schema_name.strip().upper(),
                    table_name.strip().upper(),
                    is_view,
                )
                result.append(catalog_entry.to_dict())

        return result

    def get_sqlalchemy_url(self, config: dict) -> str:
        """Concatenate a SQLAlchemy URL for use in connecting to the source.

        Args:
            config: A dict with connection parameters

        Returns:
            SQLAlchemy connection string
        """
        return ("ibm_db_sa://{}:{}@{}:{}/{}".format(
        config["username"],
        config["password"],
        config["hostname"],
        config["port"],
        config["database"],
    )        )

    @staticmethod
    def to_jsonschema_type(
        from_type: str
        | sqlalchemy.types.TypeEngine
        | type[sqlalchemy.types.TypeEngine],
    ) -> dict:
        """Returns a JSON Schema equivalent for the given SQL type.

        Developers may optionally add custom logic before calling the default
        implementation inherited from the base class.

        Args:
            from_type: The SQL type as a string or as a TypeEngine. If a TypeEngine is
                provided, it may be provided as a class or a specific object instance.

        Returns:
            A compatible JSON Schema type definition.
        """
        # Optionally, add custom logic before calling the parent SQLConnector method.
        # You may delete this method if overrides are not needed.
        return SQLConnector.to_jsonschema_type(from_type)

    @staticmethod
    def to_sql_type(jsonschema_type: dict) -> sqlalchemy.types.TypeEngine:
        """Returns a JSON Schema equivalent for the given SQL type.

        Developers may optionally add custom logic before calling the default
        implementation inherited from the base class.

        Args:
            jsonschema_type: A dict

        Returns:
            SQLAlchemy type
        """
        # Optionally, add custom logic before calling the parent SQLConnector method.
        # You may delete this method if overrides are not needed.
        return SQLConnector.to_sql_type(jsonschema_type)


class db2Stream(SQLStream):
    """Stream class for db2 streams."""

    connector_class = db2Connector
    
    def _generate_record_messages(
        self,
        record: dict,
    ) -> t.Generator[singer.RecordMessage, None, None]:
        """Write out a RECORD message.

        Args:
            record: A single stream record.

        Yields:
            Record message objects.
        
        Overrides:
            Removes conform_record_data_types - SQL records should be properly typed
        """
        pop_deselected_record_properties(record, self.schema, self.mask, self.logger)

        # Skip conform_record_data_types

        for stream_map in self.stream_maps:
            mapped_record = stream_map.transform(record)
            # Emit record if not filtered
            if mapped_record is not None:
                record_message = singer.RecordMessage(
                    stream=stream_map.stream_alias,
                    record=mapped_record,
                    version=None,
                    time_extracted=utc_now(),
                )

                yield record_message

    def get_records(self, context: dict | None) -> t.Iterable[dict[str, t.Any]]:
        """Return a generator of record-type dictionary objects.

        If the stream has a replication_key value defined, records will be sorted by the
        incremental key. If the stream also has an available starting bookmark, the
        records will be filtered for values greater than or equal to the bookmark value.

        Args:
            context: If partition context is provided, will read specifically from this
                data slice.

        Yields:
            One dict per record.

        Raises:
            NotImplementedError: If partition is passed in context and the stream does
                not support partitioning.
        """
        if context:
            msg = f"Stream '{self.name}' does not support partitioning."
            raise NotImplementedError(msg)

        selected_column_names = self.get_selected_schema()["properties"].keys()
        table = self.connector.get_table(
            full_table_name=self.fully_qualified_name,
            column_names=selected_column_names,
        )
        query = table.select()

        if self.replication_key:
            replication_key_col = table.columns[self.replication_key]
            query = query.order_by(replication_key_col)

            start_val = self.get_starting_replication_key_value(context)
            if start_val:
                # DB2 Parameters for column names not allowed
                # https://www.ibm.com/docs/en/db2/11.5?topic=design-parameters-markers
                query = query.where(
                    sqlalchemy.text(f"{replication_key_col.name} >= :start_val").bindparams(
                        start_val=start_val,
                    ),
                )
            print(f"{query}")

        if self.ABORT_AT_RECORD_COUNT is not None:
            # Limit record count to one greater than the abort threshold. This ensures
            # `MaxRecordsLimitException` exception is properly raised by caller
            # `Stream._sync_records()` if more records are available than can be
            # processed.
            query = query.limit(self.ABORT_AT_RECORD_COUNT + 1)

        with self.connector._connect() as conn:
            for record in conn.execute(query):
                yield dict(record)
