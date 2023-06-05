# tap-db2

`tap-db2` is a Singer tap for db2.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from GitHub:

```bash
pipx install git+https://github.com/ORG_NAME/tap-db2.git@main
```

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Settings

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| hostname            | True     | None    | The hostname or IP address |
| password            | True     | None    | Password    |
| username            | True     | None    | Username to connect with |
| port                | False    | 50000   | The port number |
| database            | False    | sample  | The name of the database on the host |
| stream_maps         | False    | None    | Config object for stream maps capability. For more information check out [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config   | False    | None    | User-defined config values to be used within map expressions. |

A full list of supported settings and capabilities is available by running: `tap-db2 --about`

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-db2 --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

tap-db2 requires a user account with sufficient access to query DB2 metadata tables such as `SYSCAT.TABLES` and `SELECT` access to tables that need to be synced.

## Usage

You can easily run `tap-db2` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-db2 --version
tap-db2 --help
tap-db2 --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-db2` CLI interface directly using `poetry run`:

```bash
poetry run tap-db2 --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-db2
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-db2 --version
# OR run a test `elt` pipeline:
meltano elt tap-db2 target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
