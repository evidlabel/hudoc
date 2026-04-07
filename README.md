![Deploy](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml/badge.svg)![Version](https://img.shields.io/github/v/release/evidlabel/hudoc)

# hudoc

CLI tool for downloading ECHR and GREVIO HUDOC documents

## Installation

Prefer using [uv](https://docs.astral.sh/uv/) for installation:

```sh
uv pip install .
```

## Usage

<img src="docs/assets/help.svg" alt="hudoc --help" width="800">

Example:

```sh
hudoc rss_feed.xml -o output_dir -l 5 -n 10
```

## Documentation

Run `mkdocs serve` to view the documentation locally.
