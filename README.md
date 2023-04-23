# tap-db2

[Singer](https://www.singer.io/) tap that extracts data from a [DB2](https://www.ibm.com/db2) database and produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/docs/SPEC.md). **N.B. This has only been tested against a DB2 LUW instance v10.5**

This is adapted from a fork of an MSSQL [PipelineWise](https://transferwise.github.io/pipelinewise) compatible tap connector to add a log_based replication method for use with [Change Tracking](https://docs.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-tracking-sql-server).

## How to use it

This tap has been tested with [Meltano](https://meltano.com) and can be configured as part of their ELT for the DataOps era.

If you want to run this [Singer Tap](https://singer.io) independently please read further.

## Usage

This section dives into basic usage of `tap-db2` by walking through extracting data from a table. It assumes that you can connect to and read from a DB2 database.

### Install

First, make sure Python 3 is installed on your system or follow these
installation instructions for [Mac](http://docs.python-guide.org/en/latest/starting/install3/osx/) or
[Ubuntu](https://www.digitalocean.com/community/tutorials/how-to-install-python-3-and-set-up-a-local-programming-environment-on-ubuntu-16-04).

It's recommended to use a virtualenv:

```bash
  python3 -m venv venv
  pip install tap-db2
```

or

```bash
  python3 -m venv venv
  . venv/bin/activate
  pip install --upgrade pip
  pip install .
```

### Have a source database

There's some important business data siloed in this db2 database -- we need to
extract it. Here's the table we'd like to sync:

```
> select * from example_db.animals;
+----|----------|----------------------+
| id | name     | likes_getting_petted |
+----|----------|----------------------+
|  1 | aardvark |                    0 |
|  2 | bear     |                    0 |
|  3 | cow      |                    1 |
+----|----------|----------------------+
3 rows in set (0.00 sec)
```

### Create the configuration file

Create a config file containing the database connection credentials, e.g.:

```json
{
  "host": "localhost",
  "port": "3306",
  "user": "root",
  "password": "password",
  "include_schemas_in_destination_stream_name": true
}
```

Optional:

To emit all numeric values as strings and treat floats as string data types for the target, set use_singer_decimal to true. The resulting SCHEMA message will contain an attribute in additionalProperties containing the scale and precision of the discovered property:

#### SCHEMA message
```json
"property": {
            "inclusion": "available",
            "format": "singer.decimal",
            "type": [
              "null",
              "number"
            ],
            "additionalProperties": {
              "scale_precision": "(12,0)"
            }
```

Usage:
```json
{
  "use_singer_decimal": true
}
```

Optional:

To avoid problems with uncommitted changes being read, you can set `offset_value` to add to the value found in the STATE for INCREMENTAL loads. If the value provided is for a datetime replication key then the `offset_value` is read as seconds to offset by, otherwise the value is used as provided.

Using offset_value would result in an overlapping set of records being read each time the tap is run.

Usage (offsetting by -ve 3 hours):
```json
{
  "offset_value": -10800
}
```

Optional:

To make use of fetchmany(x) instead of fetchone(), use cursor_array_size with an integer value inidicating the number of rows to pull. This can help in some architectures by pulling more rows into memory. The default if omitted is 1, the tap will still use fetchmany, but with an argument of 1, under the assumption that fetchmany(1) === fetchone().

Usage:
```json
{
  "cursor_array_size": 10000
}
```


### Discovery mode

The tap can be invoked in discovery mode to find the available tables and
columns in the database:

```bash
$ tap-db2 --config config.json --discover

```

A discovered catalog is output, with a JSON-schema description of each table. A
source table directly corresponds to a Singer stream.

```json
{
  "streams": [
    {
      "tap_stream_id": "example_db-animals",
      "table_name": "animals",
      "schema": {
        "type": "object",
        "properties": {
          "name": {
            "inclusion": "available",
            "type": [
              "null",
              "string"
            ],
            "maxLength": 255
          },
          "id": {
            "inclusion": "automatic",
            "minimum": -2147483648,
            "maximum": 2147483647,
            "type": [
              "null",
              "integer"
            ]
          },
          "likes_getting_petted": {
            "inclusion": "available",
            "type": [
              "null",
              "boolean"
            ]
          }
        }
      },
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "row-count": 3,
            "table-key-properties": [
              "id"
            ],
            "database-name": "example_db",
            "selected-by-default": false,
            "is-view": false,
          }
        },
        {
          "breadcrumb": [
            "properties",
            "id"
          ],
          "metadata": {
            "sql-datatype": "int(11)",
            "selected-by-default": true
          }
        },
        {
          "breadcrumb": [
            "properties",
            "name"
          ],
          "metadata": {
            "sql-datatype": "varchar(255)",
            "selected-by-default": true
          }
        },
        {
          "breadcrumb": [
            "properties",
            "likes_getting_petted"
          ],
          "metadata": {
            "sql-datatype": "tinyint(1)",
            "selected-by-default": true
          }
        }
      ],
      "stream": "animals"
    }
  ]
}

```

### Field selection

In sync mode, `tap-db2` consumes the catalog and looks for tables and fields
have been marked as _selected_ in their associated metadata entries.

Redirect output from the tap's discovery mode to a file so that it can be
modified:

```bash
$ tap-mssql -c config.json --discover > properties.json
```

Then edit `properties.json` to make selections. In this example we want the
`animals` table. The stream's metadata entry (associated with `"breadcrumb": []`)
gets a top-level `selected` flag, as does its columns' metadata entries. Additionally,
we will mark the `animals` table to replicate using a `FULL_TABLE` strategy. For more,
information, see [Replication methods and state file](#replication-methods-and-state-file).

```json
[
  {
    "breadcrumb": [],
    "metadata": {
      "row-count": 3,
      "table-key-properties": [
        "id"
      ],
      "database-name": "example_db",
      "selected-by-default": false,
      "is-view": false,
      "selected": true,
      "replication-method": "FULL_TABLE"
    }
  },
  {
    "breadcrumb": [
      "properties",
      "id"
    ],
    "metadata": {
      "sql-datatype": "int(11)",
      "selected-by-default": true,
      "selected": true
    }
  },
  {
    "breadcrumb": [
      "properties",
      "name"
    ],
    "metadata": {
      "sql-datatype": "varchar(255)",
      "selected-by-default": true,
      "selected": true
    }
  },
  {
    "breadcrumb": [
      "properties",
      "likes_getting_petted"
    ],
    "metadata": {
      "sql-datatype": "tinyint(1)",
      "selected-by-default": true,
      "selected": true
    }
  }
]
```

### Sync mode

With a properties catalog that describes field and table selections, the tap can be invoked in sync mode:

```bash
$ tap-db2 -c config.json --properties properties.json
```

Messages are written to standard output following the Singer specification. The
resultant stream of JSON data can be consumed by a Singer target.

```json
{"value": {"currently_syncing": "example_db-animals"}, "type": "STATE"}

{"key_properties": ["id"], "stream": "animals", "schema": {"properties": {"name": {"inclusion": "available", "maxLength": 255, "type": ["null", "string"]}, "likes_getting_petted": {"inclusion": "available", "type": ["null", "boolean"]}, "id": {"inclusion": "automatic", "minimum": -2147483648, "type": ["null", "integer"], "maximum": 2147483647}}, "type": "object"}, "type": "SCHEMA"}

{"stream": "animals", "version": 1509133344771, "type": "ACTIVATE_VERSION"}

{"record": {"name": "aardvark", "likes_getting_petted": false, "id": 1}, "stream": "animals", "version": 1509133344771, "type": "RECORD"}

{"record": {"name": "bear", "likes_getting_petted": false, "id": 2}, "stream": "animals", "version": 1509133344771, "type": "RECORD"}

{"record": {"name": "cow", "likes_getting_petted": true, "id": 3}, "stream": "animals", "version": 1509133344771, "type": "RECORD"}

{"stream": "animals", "version": 1509133344771, "type": "ACTIVATE_VERSION"}

{"value": {"currently_syncing": "example_db-animals", "bookmarks": {"example_db-animals": {"initial_full_table_complete": true}}}, "type": "STATE"}

{"value": {"currently_syncing": null, "bookmarks": {"example_db-animals": {"initial_full_table_complete": true}}}, "type": "STATE"}
```

## Replication methods and state file

In the above example, we invoked `tap-db2` without providing a _state_ file
and without specifying a replication method. The three ways to replicate a given
table are `FULL_TABLE`, `INCREMENTAL`, and `LOG_BASED`.

### Full Table

Full-table replication extracts all data from the source table each time the tap
is invoked.

### Incremental

Incremental replication works in conjunction with a state file to only extract
new records each time the tap is invoked. This requires a replication key to be
specified in the table's metadata as well.

### Log Based

Log based replication works in conjunction with a state file to extract
new and changed records that have been recorded by SQL Server Change Tracking each time the tap is invoked. This requires change tracking to be enabled on the source database as well as each table to be replicated with this method. The initial sync with this method will default to full table, and log based replication will occur on subsequent runs.

#### Examples

Let's sync the `animals` table again, but this time using incremental
replication. The replication method and replication key are set in the
table's metadata entry in properties file:

```json
{
  "streams": [
    {
      "tap_stream_id": "example_db-animals",
      "table_name": "animals",
      "schema": { ... },
      "metadata": [
        {
          "breadcrumb": [],
          "metadata": {
            "row-count": 3,
            "table-key-properties": [
              "id"
            ],
            "database-name": "example_db",
            "selected-by-default": false,
            "is-view": false,
            "replication-method": "INCREMENTAL",
            "replication-key": "id"
          }
        },
        ...
      ],
      "stream": "animals"
    }
  ]
}
```

We have no meaningful state so far, so just invoke the tap in sync mode again
without a state file:

```bash
$ tap-db2 -c config.json --properties properties.json
```

The output messages look very similar to when the table was replicated using the
default `FULL_TABLE` replication method. One important difference is that the
`STATE` messages now contain a `replication_key_value` -- a bookmark or
high-water mark -- for data that was extracted:

```json
{"type": "STATE", "value": {"currently_syncing": "example_db-animals"}}

{"stream": "animals", "type": "SCHEMA", "schema": {"type": "object", "properties": {"id": {"type": ["null", "integer"], "minimum": -2147483648, "maximum": 2147483647, "inclusion": "automatic"}, "name": {"type": ["null", "string"], "inclusion": "available", "maxLength": 255}, "likes_getting_petted": {"type": ["null", "boolean"], "inclusion": "available"}}}, "key_properties": ["id"]}

{"stream": "animals", "type": "ACTIVATE_VERSION", "version": 1509135204169}

{"stream": "animals", "type": "RECORD", "version": 1509135204169, "record": {"id": 1, "name": "aardvark", "likes_getting_petted": false}}

{"stream": "animals", "type": "RECORD", "version": 1509135204169, "record": {"id": 2, "name": "bear", "likes_getting_petted": false}}

{"stream": "animals", "type": "RECORD", "version": 1509135204169, "record": {"id": 3, "name": "cow", "likes_getting_petted": true}}

{"type": "STATE", "value": {"bookmarks": {"example_db-animals": {"version": 1509135204169, "replication_key_value": 3, "replication_key": "id"}}, "currently_syncing": "example_db-animals"}}

{"type": "STATE", "value": {"bookmarks": {"example_db-animals": {"version": 1509135204169, "replication_key_value": 3, "replication_key": "id"}}, "currently_syncing": null}}
```

Note that the final `STATE` message has a `replication_key_value` of `3`,
reflecting that the extraction ended on a record that had an `id` of `3`.
Subsequent invocations of the tap will pick up from this bookmark.

Normally, the target will echo the last `STATE` after it's finished processing
data. For this example, let's manually write a `state.json` file using the
`STATE` message:

```json
{
  "bookmarks": {
    "example_db-animals": {
      "version": 1509135204169,
      "replication_key_value": 3,
      "replication_key": "id"
    }
  },
  "currently_syncing": null
}
```

Let's add some more animals to our farm:

```
> insert into animals (name, likes_getting_petted) values ('dog', true), ('elephant', true), ('frog', false);
```

```bash
$ tap-mssql -c config.json --properties properties.json --state state.json
```

This invocation extracts any data since (and including) the
`replication_key_value`:

```json
{"type": "STATE", "value": {"bookmarks": {"example_db-animals": {"replication_key": "id", "version": 1509135204169, "replication_key_value": 3}}, "currently_syncing": "example_db-animals"}}

{"key_properties": ["id"], "schema": {"properties": {"name": {"maxLength": 255, "inclusion": "available", "type": ["null", "string"]}, "id": {"maximum": 2147483647, "minimum": -2147483648, "inclusion": "automatic", "type": ["null", "integer"]}, "likes_getting_petted": {"inclusion": "available", "type": ["null", "boolean"]}}, "type": "object"}, "type": "SCHEMA", "stream": "animals"}

{"type": "ACTIVATE_VERSION", "version": 1509135204169, "stream": "animals"}

{"record": {"name": "cow", "id": 3, "likes_getting_petted": true}, "type": "RECORD", "version": 1509135204169, "stream": "animals"}
{"record": {"name": "dog", "id": 4, "likes_getting_petted": true}, "type": "RECORD", "version": 1509135204169, "stream": "animals"}
{"record": {"name": "elephant", "id": 5, "likes_getting_petted": true}, "type": "RECORD", "version": 1509135204169, "stream": "animals"}
{"record": {"name": "frog", "id": 6, "likes_getting_petted": false}, "type": "RECORD", "version": 1509135204169, "stream": "animals"}

{"type": "STATE", "value": {"bookmarks": {"example_db-animals": {"replication_key": "id", "version": 1509135204169, "replication_key_value": 6}}, "currently_syncing": "example_db-animals"}}

{"type": "STATE", "value": {"bookmarks": {"example_db-animals": {"replication_key": "id", "version": 1509135204169, "replication_key_value": 6}}, "currently_syncing": null}}
```

---

Based on Stitch documentation
