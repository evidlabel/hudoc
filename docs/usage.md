 # Usage
 
 Run `hudoc` with the following command:
 
 ```bash
 hudoc -t <subsite> -f <rss-file> [-o <dir>] [-l <limit>] [-n <threads>] [-p]
 ```
 
 ### Command-Line Options
 
 | Option                | Description                                                                 | Default         |
 |-----------------------|-----------------------------------------------------------------------------|-----------------|
 | `-t`, `--type`        | HUDOC subsite (e.g., `echr`, `grevio`, `ecrml`, etc.) (required).            | N/A             |
 | `-f`, `--rss-file`    | Path to RSS file (required).                                                | N/A             |
 | `-o`, `--output-dir`  | Directory to save text files or evid subdirectories.                         | `data`          |
 | `-l`, `--limit`       | Number of documents to download (0 for all).                                 | 3               |
 | `-n`, `--threads`     | Number of threads for parallel downloading.                                  | 10              |
 | `-p`, `--plain`       | Save output in plain text format (default: evid format for labelling).       | False           |
 
 ### Examples
 
 Download the top 5 ECHR documents:
 
 ```bash
 hudoc -t echr -f rss_feed.xml -o output_dir -l 5 -n 10
 ```
 
 Download all documents in plain text:
 
 ```bash
 hudoc -t grevio -f rss_feed.xml -o output_dir -l 0 -p
 ```
