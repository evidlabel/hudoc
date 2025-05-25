import logging

from ..utils import get_document_text, save_text
from .constants import SUBSITE_CONFIG


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
