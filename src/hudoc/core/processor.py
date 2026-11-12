import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ..fetcher import get_document_pdf, get_document_text, is_complete_pdf
from ..writer import safe_name, save_text
from .constants import SUBSITE_CONFIG, pdf_url
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


def download_pdfs(subsite, items, output_dir, delay=3.0):
    """Save each item's official PDF in ``output_dir``; return the saved paths.

    A PDF already there is kept. Requests are ``delay`` seconds apart.
    """
    saved = []
    fetched = False
    for item in items:
        doc_id = item["doc_id"]
        path = Path(output_dir) / f"{subsite}_{safe_name(doc_id)}.pdf"
        if path.is_file():
            if is_complete_pdf(path):
                logging.info(f"{path} is already there")
                saved.append(path)
                continue
            logging.warning(f"{path} is incomplete (no %%EOF trailer); re-fetching")
        if fetched and delay > 0:
            time.sleep(delay)  # HUDOC asks for a pause between requests
        fetched = True
        if get_document_pdf(pdf_url(subsite, doc_id), path):
            logging.info(f"Saved {path}")
            saved.append(path)
    return saved


def pdf_lines(paths, evid_set=""):
    """One line per saved PDF: its path, or the evid command that keys it."""
    if evid_set:
        return [f'evid --db evid doc add -s {evid_set} "{p}"' for p in paths]
    return [str(p) for p in paths]


def _limited(items, limit):
    return items if limit == 0 else items[: min(limit, len(items))]


def _run_downloads(
    subsite, items, output_dir, limit, threads, conversion_delay, evid, delay=3.0
):
    num_items = len(items)
    items = _limited(items, limit)
    logging.info(f"Processing {len(items)} of {num_items} items for subsite {subsite}")

    def one(index, item):
        if index and delay > 0 and threads <= 1:
            time.sleep(delay)  # HUDOC asks for a pause between requests
        download_document(item, subsite, output_dir, conversion_delay, evid=evid)
        if threads > 1 and delay > 0:
            time.sleep(delay)

    if threads <= 1:
        for index, item in enumerate(items):
            one(index, item)
        return
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(one, i, item) for i, item in enumerate(items)]
        for future in futures:
            future.result()


def _process(
    subsite,
    items,
    output_dir,
    limit,
    threads,
    conversion_delay,
    evid,
    delay,
    pdf,
    evid_set,
):
    if not subsite:
        logging.error("Failed to detect subsite or parse items")
        return []
    if not items:
        logging.error("No items to process")
        return []
    if pdf:
        paths = download_pdfs(subsite, _limited(items, limit), output_dir, delay)
        lines = pdf_lines(paths, evid_set)
        for line in lines:
            print(line)
        return lines
    _run_downloads(
        subsite, items, output_dir, limit, threads, conversion_delay, evid, delay
    )
    return []


def process_rss(
    rss_file,
    output_dir,
    limit=3,
    threads=1,
    conversion_delay=2.0,
    evid=False,
    delay=3.0,
    pdf=False,
    evid_set="",
):
    """Process an RSS file: download each item's text, or with ``pdf`` its official PDF."""
    subsite, items = parse_rss_file(rss_file)
    return _process(
        subsite,
        items,
        output_dir,
        limit,
        threads,
        conversion_delay,
        evid,
        delay,
        pdf,
        evid_set,
    )


def process_rss_url(
    url,
    output_dir,
    limit=3,
    threads=1,
    conversion_delay=2.0,
    evid=False,
    delay=3.0,
    pdf=False,
    evid_set="",
):
    """Fetch an RSS feed: download each item's text, or with ``pdf`` its official PDF."""
    subsite, items = parse_rss_url(url)
    return _process(
        subsite,
        items,
        output_dir,
        limit,
        threads,
        conversion_delay,
        evid,
        delay,
        pdf,
        evid_set,
    )
