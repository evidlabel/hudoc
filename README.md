![Tests](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml/badge.svg)](https://github.com/evidlabel/hudoc/actions/workflows/ci.yml) ![Version](https://img.shields.io/github/v/release/evidlabel/hudoc)
# hudoc

A CLI tool for downloading documents from various HUDOC databases (e.g., ECHR, GREVIO, ECRML, and others) using RSS feeds.

## Features

- Download documents from multiple HUDOC subsites (e.g., ECHR, GREVIO, COMMHR, CPT, ECRI, ECRML, ESC, EXEC, FCNM, GRECO, GRETA) as plain text or in evid format (LaTeX and YAML).
- Support for RSS feeds with parallel downloading.
- Triggers on-demand document conversion to HTML if direct download fails.
- Customizable output directory, conversion delay, and verbose logging.
- Modular codebase with separate modules for parsing, downloading, and processing.

## Installation

1. **Install UV**:
   ```bash
   pip install uv
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/hudoc.git
   cd hudoc
   ```

3. **Install dependencies**:
   ```bash
   uv pip install .
   ```

4. **Set up Fish shell completion (optional)**:
   To make `hudoc` available as a command with tab completion:
   ```bash
   mkdir -p ~/.config/fish/completions
   cp hudoc.fish ~/.config/fish/completions/
   ```
   This enables `hudoc` in all new Fish shell sessions. To apply immediately:
   ```fish
   source ~/.config/fish/completions/hudoc.fish
   ```
   Alternatively, add to `~/.config/fish/config.fish`:
   ```fish
   source /path/to/hudoc.fish
   ```

## Usage

Run the `hudoc` command to download documents from an RSS file:

```bash
hudoc -t <subsite> -r <rss-file> [-o <dir>] [-f] [-n <threads>] [-d <seconds>] [-v] [-e]
```

### Options

- `-t`, `--type <subsite>`: Required. Specify the HUDOC subsite (e.g., `echr`, `grevio`, `ecrml`, `commhr`, etc.).
- `-r`, `--rss-file <path>`: Required. Path to an RSS file.
- `-o`, `--output-dir <dir>`: Directory to save text files or evid subdirectories (default: `data`).
- `-f`, `--full`: Download all documents from RSS feed (default: top 3).
- `-n`, `--threads <n>`: Number of threads for parallel downloading (default: 10).
- `-d`, `--conversion-delay <seconds>`: Delay (seconds) after triggering document conversion if direct download fails (default: 2.0).
- `-v`, `--verbose`: Enable detailed logging for debugging.
- `-e`, `--evid`: Save output in evid format (LaTeX and YAML) instead of plain text.

### Examples

**Download top 3 ECHR documents from an RSS file**:
```bash
hudoc -t echr -r tests/data/echr_rss.xml
```

**Download all GREVIO documents with 5 threads**:
```bash
hudoc -t grevio -r tests/data/grevio_rss.xml -f -n 5 -o grevio_cases
```

**Download ECHR documents in evid format with 5s conversion delay**:
```bash
hudoc -t echr -r tests/data/echr_rss.xml -e -d 5
```

## Documentation

For detailed documentation, build and serve the MkDocs site:
```bash
uv pip install --with dev  # Install dev dependencies
uv run mkdocs serve
```
Open `http://localhost:8000` in your browser to view the documentation.

## Development

### Project Structure

- `src/hudoc/`:
  - `cli.py`: Command-line interface and argument parsing.
  - `utils.py`: Utilities for fetching (`get_document_text`), triggering conversion (`trigger_document_conversion`), and saving (`save_text`, `save_evid`) document content.
  - `core/`:
    - `constants.py`: Subsite configurations (URLs, ID keys, library codes).
    - `parser.py`: Parses RSS files (`parse_rss_file`).
    - `downloader.py`: Handles document downloading (`download_document`).
    - `processor.py`: Orchestrates RSS processing.
- `tests/`:
  - `test_core.py`: Tests for parsing and processing logic.
  - `test_utils.py`: Tests for utility functions.
  - `data/`:
    - Sample RSS and HTML files for testing.

### Running Tests

Install development dependencies:
```bash
uv pip install --with dev
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
- **Document download failures**: Check the RSS file and network connectivity. Use `--verbose` for detailed logs. If conversion is needed, the tool triggers it only if the direct download fails; try increasing `--conversion-delay` if issues persist.
- **Empty documents**: Some HUDOC documents may lack text content or fail to convert. The tool logs warnings and retries up to 3 times if the direct download is empty or fails.

## License

MIT License. See [LICENSE](LICENSE) for details.
