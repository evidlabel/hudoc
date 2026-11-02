[![CI](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml/badge.svg)](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/evidlabel/hudoc)](https://github.com/evidlabel/hudoc/releases)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/licenses/MIT)

# hudoc

CLI tool for downloading ECHR and GREVIO HUDOC documents.

Agent-oriented usage: see **[`SKILL.md`](SKILL.md)** in this directory.

## Installation

Prefer using [uv](https://docs.astral.sh/uv/) for installation:

```sh
uv pip install .
```

## Usage

<img src="docs/assets/help.svg" alt="hudoc --help" width="800">

Fetch one latest ECtHR document (live HUDOC query):

```sh
hudoc latest -s echr -l 1 --plain
```

Same as `sh examples/latest.sh`.

Print the official PDF of a judgment, the version to key in evid (pages, headers, footnotes):

```sh
hudoc pdf 001-218240 --set <evid-set>
```

## License

This project is licensed under the [MIT License](LICENSE).
