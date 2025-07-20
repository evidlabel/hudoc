# Usage

Run `hudoc` with the following command:

```bash
hudoc <rss-file> [-o <dir>] [-l <limit>] [-n <threads>] [-p]
```

### Command-Line Options

| Option                | Description                                                                 | Default         |
|-----------------------|-----------------------------------------------------------------------------|-----------------|
| `<rss-file>`          | Path to RSS file (required).                                                | N/A             |
| `-o`, `--output-dir`  | Directory to save text files or evid subdirectories.                         | `data`          |
| `-l`, `--limit`       | Number of documents to download (0 for all).                                 | 3               |
| `-n`, `--threads`     | Number of threads for parallel downloading.                                  | 10              |
| `-p`, `--plain`       | Save output in plain text format (default: evid format for labelling).       | False           |

Note: The HUDOC subsite is automatically detected from the RSS file URLs.

### Examples

Download the top 5 ECHR documents:

```bash
hudoc rss_feed.xml -o output_dir -l 5 -n 10
```

Download all documents in plain text:

```bash
hudoc rss_feed.xml -o output_dir -l 0 -p
```
