 # hudoc documentation
 
 Welcome to the documentation for `hudoc`, a command-line tool for downloading documents from various HUDOC databases (e.g., ECHR, GREVIO, ECRML, COMMHR, and others) using RSS files.
 
 ## Overview
 
 `hudoc` is a Python-based CLI tool designed to fetch documents from HUDOC databases using RSS feeds. It supports parallel downloading, on-demand document conversion, customizable output, and robust error handling, making it suitable for researchers, legal professionals, and developers.
 
 Key features:
 
 - Supports multiple HUDOC subsites (e.g., ECHR, GREVIO, COMMHR, CPT, ECRI, ECRML, ESC, EXEC, FCNM, GRECO, GRETA) with subsite-specific document identifiers.
 - Triggers on-demand conversion to HTML only if direct download fails or returns empty content.
 - Extracts plain text from HTML documents, preserving formatting.
 - Outputs in plain text or evid format (LaTeX and YAML).
 - Modular design with separate modules for parsing, downloading, and processing.
 - Utilizes NumPy for vectorized data operations (where applicable).
 - Tested with realistic data in `tests/data/`.
 
 The codebase uses `uv` for dependency management and installation, replacing traditional tools like Poetry for faster performance.
