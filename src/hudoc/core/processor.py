import logging
from concurrent.futures import ThreadPoolExecutor

from ..fetcher import get_document_text
from ..writer import save_text
from .constants import SUBSITE_CONFIG
from .parser import parse_rss_file, parse_rss_url


def download_document(item, hudoc_type, output_dir, conversion_delay, evid=False):
    config = SUBSITE_CONFIG[hudoc_type]
    base_url = config["base_url"]
    library = config["library"]
    doc_id = item["doc_id"]
    rss_link = item.get("rss_link")
    text = get_document_text(doc_id, base_url, library, rss_link, conversion_delay)
    if text:
        save_text(
            text,
            doc_id,
            item["title"],
            item["description"],
            output_dir,
            hudoc_type,
            verdict_date=item.get("verdict_date"),
            evid=evid,
        )
    else:
        logging.warning(f"No content retrieved for {doc_id}")


def _run_downloads(subsite, items, output_dir, limit, threads, conversion_delay, evid):
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
                subsite,
                output_dir,
                conversion_delay,
                evid=evid,
            )
            for item in items
        ]
        for future in futures:
            future.result()


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
    _run_downloads(subsite, items, output_dir, limit, threads, conversion_delay, evid)


def process_rss_url(
    url, output_dir, limit=3, threads=10, conversion_delay=2.0, evid=False
):
    """Fetch RSS from URL, detect subsite, and download documents in parallel."""
    subsite, items = parse_rss_url(url)
    if not subsite:
        logging.error("Failed to detect subsite or parse items")
        return
    if not items:
        logging.error("No items to process")
        return
    _run_downloads(subsite, items, output_dir, limit, threads, conversion_delay, evid)
