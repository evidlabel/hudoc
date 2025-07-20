# Technical Details

## RSS Parsing

The `parse_rss_file` function uses `xml.etree.ElementTree` to parse RSS feeds, extracting subsite-specific document IDs (e.g., `itemid` for ECHR, `greviosectionid` for GREVIO, `ecrmlid` for ECRML) from link fragments. It handles malformed XML and missing fields gracefully. Subsite is auto-detected from the URL in the RSS file.

## Document Downloading

Documents are fetched using `requests` by first attempting a direct download. If the direct download fails (e.g., HTTP error) or returns empty content, the `trigger_document_conversion` function sends a request to the RSS link URL to initiate HTML conversion, followed by a fixed delay of 2 seconds. Text is parsed with `BeautifulSoup` from `<p>`, `<li>`, `<h1>`, `<h2>`, and `<h3>` elements and saved with metadata (title, description) in plain text or evid format.

## Parallel Processing

RSS processing uses `ThreadPoolExecutor` for parallel downloads, with a configurable thread count (default: 10).

## Vectorization with NumPy

NumPy is included for potential vectorized operations on document metadata or text processing in future enhancements, enabling efficient batch handling of large datasets.
