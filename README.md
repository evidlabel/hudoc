[![CI](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml/badge.svg)](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/evidlabel/hudoc)](https://github.com/evidlabel/hudoc/releases)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

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
