# hudoc

A CLI tool for downloading documents from the ECHR and GREVIO HUDOC databases using RSS feeds or single document links.

## Installation

1. Install Poetry:
   ```bash
   pip install poetry
   ```

2. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd hudoc
   ```

3. Install dependencies:
   ```bash
   poetry install
   ```

4. Activate the virtual environment:
   ```bash
   poetry shell
   ```

## Usage

Run the `hudoc` command with options to download ECHR or GREVIO documents:

```bash
hudoc --type <echr|grevio> [--rss-file <path> | --link <url>] [--output-dir <dir>] [--full] [--threads <n>] [--verbose]
```

### Options

- `--type`: Required. Specify `echr` or `grevio` for the HUDOC database.
- `--rss-file`: Path to an RSS file (mutually exclusive with `--link`).
- `--link`: URL of a single document (mutually exclusive with `--rss-file`).
- `--output-dir`: Directory to save text files (default: `data`).
- `--full`: Download all documents from RSS (default: top 3).
- `--threads`: Number of threads for parallel downloading (default: 10, RSS only).
- `--verbose`: Enable detailed logging.

### Examples

Download top 3 ECHR documents from an RSS file:
```bash
hudoc --type echr --rss-file echr_short.xml
```

Download all GREVIO documents with 5 threads:
```bash
hudoc --type grevio --rss-file grevio_short.xml --full --threads 5 --output-dir grevio_cases
```

Download a single ECHR document:
```bash
hudoc --type echr --link "http://hudoc.echr.coe.int/eng#{\"itemid\":[\"001-243083\"]}"
```

## Documentation

Build and view documentation using MkDocs:
```bash
poetry install --with dev
poetry run mkdocs serve
```
Open `http://localhost:8000` in your browser to view the docs.

## Development

### Running Tests

Install development dependencies:
```bash
poetry install --with dev
```

Run tests with pytest:
```bash
poetry run pytest
```

### Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

MIT License. See LICENSE for details.
