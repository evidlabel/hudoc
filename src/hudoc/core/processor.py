import logging
import requests
import tempfile
import os
from concurrent.futures import ThreadPoolExecutor

from .parser import parse_rss_file, parse_link
from .downloader import download_document, ECHR_BASE_URL, GREVIO_BASE_URL, LIBRARY

DEFAULT_LIMIT = 3

def process_rss(hudoc_type, rss_file, output_dir, full, threads):
    """Process RSS file and download documents in parallel.

    Args:
        hudoc_type (str): Type of HUDOC database ('echr' or 'grevio').
        rss_file (str): Path to the RSS file.
        output_dir (str): Directory to save text files.
        full (bool): If True, download all documents; else, top 3.
        threads (int): Number of threads for parallel downloading.
    """
    items = parse_rss_file(rss_file, hudoc_type)
    if not items:
        logging.error("No items to process")
        return

    limit = len(items) if full else min(DEFAULT_LIMIT, len(items))
    items = items[:limit]
    logging.info(f"Processing {limit} of {len(items)} items")

    base_url = ECHR_BASE_URL if hudoc_type == "echr" else GREVIO_BASE_URL
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(
                download_document,
                item,
                base_url,
                LIBRARY[hudoc_type],
                output_dir,
                hudoc_type
            )
            for item in items
        ]
        for future in futures:
            future.result()  # Wait for completion, handle exceptions

def process_rss_link(hudoc_type, link, output_dir, full, threads):
    """Process an RSS feed URL and download documents in parallel.

    Args:
        hudoc_type (str): Type of HUDOC database ('echr' or 'grevio').
        link (str): RSS feed URL.
        output_dir (str): Directory to save text files.
        full (bool): If True, download all documents; else, top 3.
        threads (int): Number of threads for parallel downloading.
    """
    try:
        response = requests.get(link, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch RSS feed from {link}: {str(e)}")
        return

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as temp_file:
        temp_file.write(response.text)
        temp_file_path = temp_file.name

    try:
        process_rss(hudoc_type, temp_file_path, output_dir, full, threads)
    finally:
        os.unlink(temp_file_path)  # Clean up temporary file

def process_link(hudoc_type, link, output_dir):
    """Process a single document link and download the document.

    Args:
        hudoc_type (str): Type of HUDOC database ('echr' or 'grevio').
        link (str): URL of the document.
        output_dir (str): Directory to save the text file.
    """
    items = parse_link(hudoc_type, link)
    if not items:
        logging.error("No document to process")
        return

    base_url = ECHR_BASE_URL if hudoc_type == "echr" else GREVIO_BASE_URL
    item = items[0]
    download_document(item, base_url, LIBRARY[hudoc_type], output_dir, hudoc_type)
