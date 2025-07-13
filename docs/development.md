 # Development
 
 ## Codebase Structure
 
 The `hudoc` codebase is organized for modularity and maintainability:
 
 - **src/hudoc/cli.py**: Parses command-line arguments and orchestrates execution.
 - **src/hudoc/utils.py**: Contains functions for fetching (`get_document_text`), triggering conversion (`trigger_document_conversion`), and saving (`save_text`, `save_evid`) document content.
 - **src/hudoc/core/**:
   - **constants.py**: Defines subsite configurations (URLs, document ID keys, library codes).
   - **parser.py**: Parses RSS files (`parse_rss_file`).
   - **downloader.py**: Downloads and saves documents (`download_document`).
   - **processor.py**: Processes RSS files (`process_rss`).
 - **tests/**: Contains unit tests and sample data in `tests/data/`.
 
 ## Setting Up
 
 Install development dependencies:
 ```bash
 uv pip install ".[dev]"
 ```
 
 ## Running Tests
 
 Run tests with pytest:
 ```bash
 uv run pytest
 ```
 
 Tests use pre-downloaded RSS and HTML files in `tests/data/` to simulate real-world inputs. HTTP requests are mocked using `requests-mock` to avoid live API calls. The test suite covers:
 
 - RSS parsing (`test_parse_rss_file_echr`, `test_parse_rss_file_grevio`).
 - RSS processing (`test_process_rss_echr`).
 - Utility functions (`test_get_document_text`, `test_save_text_echr`, `test_save_text_grevio`, `test_save_evid_echr`).
 
 Note: Some subsite-specific tests (e.g., GREVIO processing) are currently skipped due to ongoing validation of real-world RSS formats.
 
 ## Linting
 
 Run ruff to check code style:
 ```bash
 uv run ruff check .
 ```
 
 Fix issues automatically:
 ```bash
 uv run ruff check --fix .
 ```
 
 ## Contributing
 
 Follow the [contributing guidelines](../README.md#contributing) to submit pull requests.
