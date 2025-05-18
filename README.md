[![Tests](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml/badge.svg)](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml) ![Version](https://img.shields.io/github/v/release/evidlabel/hudoc)
# hudoc

A CLI tool for downloading documents from the European Court of Human Rights (ECHR) and Group of Experts on Action against Violence against Women and Domestic Violence (GREVIO) HUDOC databases using RSS feeds or single document links.

## Features

- Download ECHR and GREVIO documents as plain text files.
- Support for RSS feeds or individual document URLs.
- Parallel downloading with configurable threads.
- Customizable output directory and verbose logging.
- Modular codebase with separate modules for parsing, downloading, and processing.

## Installation

1. **Install Poetry**:
   ```bash
   pip install poetry
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/hudoc.git
   cd hudoc
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Activate the virtual environment**:
   ```bash
   poetry shell
   ```

## Usage

Run the `hudoc` command to download documents:

```bash
hudoc --type <echr|grevio> [--rss-file <path> | --link <url>] [--output-dir <dir>] [--full] [--threads <n>] [--verbose]
```

### Options

- `--type <echr|grevio>`: Required. Specify the HUDOC database (`echr` or `grevio`).
- `--rss-file <path>`: Path to an RSS file (mutually exclusive with `--link`).
- `--link <url>`: URL of a single document or RSS feed (mutually exclusive with `--rss-file`).
- `--output-dir <dir>`: Directory to save text files (default: `data`).
- `--full`: Download all documents from RSS feed (default: top 3).
- `--threads <n>`: Number of threads for parallel downloading (default: 10, RSS only).
- `--verbose`: Enable detailed logging for debugging.

### Examples

**Download top 3 ECHR documents from an RSS file**:
```bash
hudoc --type echr --rss-file tests/data/echr_rss.xml
```

**Download all GREVIO documents with 5 threads**:
```bash
hudoc --type grevio --rss-file tests/data/grevio_rss.xml --full --threads 5 --output-dir grevio_cases
```

**Download a single ECHR document**:
```bash
hudoc --type echr --link "http://hudoc.echr.coe.int/eng#{\"itemid\":[\"001-243083\"]}"
```

**Download from an RSS feed URL**:
```bash
hudoc --type grevio --link "https://hudoc.grevio.coe.int/app/transform/rss?library=grevioeng&query=test"
```

## Documentation

For detailed documentation, build and serve the MkDocs site:
```bash
poetry install --with dev
poetry run mkdocs serve
```
Open `http://localhost:8000` in your browser to view the documentation.

## Development

### Project Structure

- `src/hudoc/`:
  - `cli.py`: Command-line interface and argument parsing.
  - `utils.py`: Utilities for fetching and saving document text.
  - `core/`:
    - `parser.py`: Parses RSS files and document links.
    - `downloader.py`: Handles document downloading.
    - `processor.py`: Orchestrates RSS and link processing.
- `tests/`:
  - `test_core.py`: Tests for parsing and processing logic.
  - `test_utils.py`: Tests for utility functions.
  - `data/`:
    - Sample RSS and HTML files for testing.

### Running Tests

Install development dependencies:
```bash
poetry install --with dev
```

Run tests with pytest:
```bash
pytest
```

Tests use pre-downloaded data in `tests/data/` to simulate real-world inputs. HTTP requests are mocked to avoid live API calls.

### Linting

Check code style with flake8:
```bash
flake8 src tests
```

### Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

### Troubleshooting

- **RSS parsing errors**: Ensure the RSS file is valid XML and contains `itemid` (ECHR) or `greviosectionid` (GREVIO) in the link fragment.
- **Document download failures**: Check the URL and network connectivity. Use `--verbose` for detailed logs.
- **Empty documents**: Some HUDOC documents may lack text content. The tool logs warnings for these cases.

## License

MIT License. See [LICENSE](LICENSE) for details.
