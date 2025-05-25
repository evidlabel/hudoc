[![Tests](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml/badge.svg)](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml) ![Version](https://img.shields.io/github/v/release/evidlabel/hudoc)
# hudoc

A CLI tool for downloading documents from various HUDOC databases (e.g., ECHR, GREVIO, ECRML, and others) using RSS feeds or single document links.

## Features

- Download documents from multiple HUDOC subsites (e.g., ECHR, GREVIO, COMMHR, CPT, ECRI, ECRML, ESC, EXEC, FCNM, GRECO, GRETA) as plain text or in evid format (LaTeX and YAML).
- Support for RSS feeds or individual document URLs.
- Parallel downloading with configurable threads.
- Triggers on-demand document conversion to HTML only if direct download fails.
- Customizable output directory, conversion delay, and verbose logging.
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
hudoc --type <subsite> [--rss-file <path> | --link <url>] [--output-dir <dir>] [--full] [--threads <n>] [--conversion-delay <seconds>] [--verbose] [--evid]
```

### Options

- `--type <subsite>`: Required. Specify the HUDOC subsite (e.g., `echr`, `grevio`, `ecrml`, `commhr`, etc.).
- `--rss-file <path>`: Path to an RSS file (mutually exclusive with `--link`).
- `--link <url>`: URL of a single document or RSS feed (mutually exclusive with `--rss-file`).
- `--output-dir <dir>`: Directory to save text files or evid subdirectories (default: `data`).
- `--full`: Download all documents from RSS feed (default: top 3).
- `--threads <n>`: Number of threads for parallel downloading (default: 10, RSS only).
- `--conversion-delay <seconds>`: Delay (seconds) after triggering document conversion if direct download fails (default: 2.0).
- `--verbose`: Enable detailed logging for debugging.
- `--evid`: Save output in evid format (LaTeX with full document text and YAML) instead of plain text.

### Examples

**Download top 3 ECHR documents from an RSS file**:
```bash
hudoc --type echr --rss-file tests/data/echr_rss.xml
```

**Download all GREVIO documents with 5 threads**:
```bash
hudoc --type grevio --rss-file tests/data/grevio_rss.xml --full --threads 5 --output-dir grevio_cases
```

**Download a single ECRML document in evid format with 5s conversion delay**:
```bash
hudoc --type ecrml --link "http://hudoc.ecrml.coe.int/eng#{\"ecrmlid\":[\"TEST-ECRML-001\"]}" --evid --conversion-delay 5
```

**Download from an RSS feed URL for COMMHR**:
```bash
hudoc --type commhr --link "https://hudoc.commhr.coe.int/app/transform/rss?library=COMMHR&query=test"
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
  - `utils.py`: Utilities for fetching (`get_document_text`), triggering conversion (`trigger_document_conversion`), and saving (`save_text`, `save_evid`) document content.
  - `core/`:
    - `constants.py`: Subsite configurations (URLs, ID keys, library codes).
    - `parser.py`: Parses RSS files (`parse_rss_file`) and document links (`parse_link`).
    - `downloader.py`: Handles document downloading (`download_document`).
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

Check code style with ruff:
```bash
ruff check .
```

Fix linting issues automatically:
```bash
ruff check --fix .
```

### Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

### Troubleshooting

- **RSS parsing errors**: Ensure the RSS file is valid XML and contains the appropriate document ID key (e.g., `itemid` for ECHR, `greviosectionid` for GREVIO, `ecrmlid` for ECRML).
- **Document download failures**: Check the URL and network connectivity. Use `--verbose` for detailed logs. If conversion is needed, the tool triggers it only if the direct download fails; try increasing `--conversion-delay` if issues persist.
- **Empty documents**: Some HUDOC documents may lack text content or fail to convert. The tool logs warnings and retries up to 3 times if the direct download is empty or fails.

## License

MIT License. See [LICENSE](LICENSE) for details.
