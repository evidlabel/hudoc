# hudoc Documentation

Welcome to the documentation for `hudoc`, a command-line tool for downloading documents from the ECHR and GREVIO HUDOC databases.

## Overview

`hudoc` is a Python-based CLI tool designed to fetch documents from the HUDOC databases using RSS feeds or individual document URLs. It supports parallel downloading, customizable output, and robust error handling, making it suitable for researchers, legal professionals, and developers.

Key features:

- Supports both ECHR (`itemid`) and GREVIO (`greviosectionid`) document identifiers.
- Extracts plain text from HTML documents, preserving formatting.
- Outputs in plain text or evid format (LaTeX and YAML).
- Modular design with separate modules for parsing, downloading, and processing.
- Tested with realistic data in `tests/data/`.

## Installation

See the [README](../README.md#installation) for installation instructions using Poetry.

## Usage

Run `hudoc` with the following command:

```bash
hudoc --type <echr|grevio> [--rss-file <path> | --link <url>] [--output-dir <dir>] [--full] [--threads <n>] [--verbose] [--evid]
```

### Command-Line Options

| Option            | Description                                                                 | Default         |
MD|-------------------|-----------------------------------------------------------------------------|-----------------|
MD| `--type`          | HUDOC database: `echr` or `grevio` (required).                               | N/A             |
MD| `--rss-file`      | Path to RSS file (mutually exclusive with `--link`).                         | N/A             |
MD| `--link`          | URL of a single document or RSS feed (mutually exclusive with `--rss-file`). | N/A             |
MD| `--output-dir`    | Directory to save text files or evid subdirectories.                         | `data`          |
MD| `--full`          | Download all documents from RSS (otherwise, top 3).                          | False           |
MD| `--threads`       | Number of threads for parallel downloading (RSS only).                       | 10              |
MD| `--verbose`       | Enable detailed logging.                                                     | False           |
MD| `--evid`          | Save output in evid format (LaTeX and YAML) instead of plain text.           | False           |

### Examples

See the [README](../README.md#examples) for usage examples.

## Codebase Structure

The `hudoc` codebase is organized for modularity and maintainability:

- **src/hudoc/cli.py**: Parses command-line arguments and orchestrates execution.
- **src/hudoc/utils.py**: Contains functions for fetching (`get_document_text`) and saving (`save_text`, `save_evid`) document content.
- **src/hudoc/core/**:
  - **parser.py**: Parses RSS files (`parse_rss_file`) and document links (`parse_link`).
  - **downloader.py**: Downloads and saves documents (`download_document`).
  - **processor.py**: Processes RSS files (`process_rss`), RSS URLs (`process_rss_link`), and single links (`process_link`).
- **tests/**: Contains unit tests and sample data in `tests/data/`.

## Development

### Setting Up

Install development dependencies:
```bash
poetry install --with dev
```

### Running Tests

Run tests with pytest:
```bash
pytest
```

Tests use pre-downloaded RSS and HTML files in `tests/data/` to simulate real-world inputs. HTTP requests are mocked using `requests-mock` to avoid live API calls. The test suite covers:

- RSS parsing (`test_parse_rss_file_echr`, `test_parse_rss_file_grevio`).
- Link parsing (`test_parse_link_echr`, `test_parse_link_grevio`).
- RSS processing (`test_process_rss_echr`).
- Utility functions (`test_get_document_text`, `test_save_text_echr`, `test_save_text_grevio`, `test_save_evid_echr`).

Note: The GREVIO link processing test (`test_process_link_grevio`) is currently skipped due to ongoing validation of real-world GREVIO link formats.

### Linting

Run ruff to check code style:
```bash
ruff check .
```

Fix issues automatically:
```bash
ruff check --fix .
```

### Contributing

Follow the [contributing guidelines](../README.md#contributing) to submit pull requests.

## Technical Details

### RSS Parsing

The `parse_rss_file` function uses `xml.etree.ElementTree` to parse RSS feeds, extracting `itemid` (ECHR) or `greviosectionid` (GREVIO) from link fragments. It handles malformed XML and missing fields gracefully.

### Link Parsing

The `parse_link` function extracts document IDs from URL fragments, normalizing JSON data and handling both list and string formats for IDs.

### Document Downloading

Documents are fetched using `requests` and parsed with `BeautifulSoup` to extract text from `<p>`, `<li>`, `<h1>`, `<h2>`, and `<h3>` elements. Text is saved with metadata (title, description for GREVIO) in plain text or evid format.

### Parallel Processing
CFviation:

RSS processing uses `ThreadPoolExecutor` for parallel downloads, with a configurable thread count (default: 10). Single document downloads are sequential.

## Troubleshooting

See the [README](../README.md#troubleshooting) for common issues and solutions.

## License

MIT License. See [LICENSE](../LICENSE) for details.
