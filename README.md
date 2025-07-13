 # hudoc
 
 CLI tool for downloading ECHR and GREVIO HUDOC documents
 
 ## Installation
 
 Prefer using [uv](https://docs.astral.sh/uv/) for installation:
 
 ```sh
 uv pip install .
 ```
 
 Alternatively, use pip:
 
 ```sh
 pip install .
 ```
 
 For development dependencies (including tests and mkdocs):
 
 ```sh
 uv pip install .[dev]
 ```
 
 ## Usage
 
 ```sh
 hudoc --help
 ```
 
 Example:
 
 ```sh
 hudoc -t echr -r rss_feed.xml -o output_dir -f -n 5
 ```
 
 ## Documentation
 
 Run `mkdocs serve` to view the documentation locally.
