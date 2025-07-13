# hudoc

CLI tool for downloading ECHR and GREVIO HUDOC documents

## Installation

Prefer using uv for installation:

```bash
uv pip install hudoc
```

For development dependencies (including mkdocs for documentation):

```bash
uv pip install -e ".[dev]"
```

## Usage

```bash
hudoc --help
```

Example:

```bash
hudoc -t echr -r rss_feed.xml -o output_dir -f -n 5
```

## Documentation

Build and serve documentation using mkdocs:

```bash
mkdocs serve
```
