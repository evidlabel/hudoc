import logging
from concurrent.futures import ThreadPoolExecutor

from .downloader import download_document
from .parser import parse_rss_file


def process_rss(
    rss_file, output_dir, limit=3, threads=10, conversion_delay=2.0, evid=False
):
    """Process RSS file, detect subsite, and download documents in parallel."""
    subsite, items = parse_rss_file(rss_file)
    if not subsite:
        logging.error("Failed to detect subsite or parse items")
        return

    if not items:
        logging.error("No items to process")
        return

    num_items = len(items)
    if limit == 0:
        limit = num_items
    else:
        limit = min(limit, num_items)
    items = items[:limit]
    logging.info(f"Processing {limit} of {num_items} items for subsite {subsite}")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(
                download_document,
                item,
                subsite,  # Use detected subsite
                output_dir,
                conversion_delay,
                evid=evid,
            )
            for item in items
        ]
        for future in futures:
            future.result()  # Wait for completion, handle exceptions
