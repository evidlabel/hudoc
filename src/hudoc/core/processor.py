import logging
from concurrent.futures import ThreadPoolExecutor

from .downloader import download_document
from .parser import parse_rss_file

DEFAULT_LIMIT = 3


def process_rss(
    hudoc_type, rss_file, output_dir, download_all, threads, conversion_delay, evid=False
):
    """Process RSS file and download documents in parallel.

    Args:
        hudoc_type (str): HUDOC subsite (e.g., echr, grevio, ecrml).
        rss_file (str): Path to the RSS file.
        output_dir (str): Directory to save text files.
        download_all (bool): If True, download all documents; else, top 3.
        threads (int): Number of threads for parallel downloading.
        conversion_delay (float): Delay (seconds) after triggering document conversion.
        evid (bool): If True, save in evid format; else plain text.

    """
    items = parse_rss_file(rss_file, hudoc_type)
    if not items:
        logging.error("No items to process")
        return

    limit = len(items) if download_all else min(DEFAULT_LIMIT, len(items))
    items = items[:limit]
    logging.info(f"Processing {limit} of {len(items)} items")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(
                download_document,
                item,
                hudoc_type,
                output_dir,
                conversion_delay,
                evid=evid,
            )
            for item in items
        ]
        for future in futures:
            future.result()  # Wait for completion, handle exceptions
