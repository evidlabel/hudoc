import logging
import xml.etree.ElementTree as ET
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

from .utils import get_document_text, save_text


ECHR_BASE_URL = "https://hudoc.echr.coe.int/app/conversion/docx/html/body"
GREVIO_BASE_URL = "https://hudoc.grevio.coe.int/app/conversion/docx/html/body"
LIBRARY = {"echr": "ECHR", "grevio": "GREVIO"}
DEFAULT_LIMIT = 3


def parse_rss_file(rss_file, hudoc_type):
    """Parse RSS file and extract document IDs, titles, and descriptions."""
    try:
        tree = ET.parse(rss_file)
        root = tree.getroot()
        items = []
        id_key = "itemid" if hudoc_type == "echr" else "greviosectionid"
        for item in root.findall(".//item"):
            link = item.find("link").text
            title = item.find("title").text or "Untitled"
            description = item.find("description").text or "No description" if hudoc_type == "grevio" else None
            try:
                fragment = link.split("#")[1]
                fragment = urllib.parse.unquote(fragment)
                data = json.loads(fragment)
                doc_id = data[id_key][0]
                items.append({"doc_id": doc_id, "title": title, "description": description})
            except (IndexError, json.JSONDecodeError, KeyError) as e:
                logging.warning(f"Failed to parse {id_key} from link {link}: {str(e)}")
                continue
        logging.info(f"Parsed {len(items)} items from RSS file")
        return items
    except ET.ParseError as e:
        logging.error(f"Failed to parse RSS file: {str(e)}")
        return []
    except FileNotFoundError:
        logging.error(f"RSS file not found: {rss_file}")
        return []


def parse_link(link, hudoc_type):
    """Parse a single document link to extract doc_id, with dummy title and description."""
    id_key = "itemid" if hudoc_type == "echr" else "greviosectionid"
    try:
        fragment = link.split("#")[1]
        fragment = urllib.parse.unquote(fragment)
        data = json.loads(fragment)
        doc_id = data[id_key][0]
        return [{"doc_id": doc_id, "title": "Untitled", "description": "No description"}]
    except (IndexError, json.JSONDecodeError, KeyError) as e:
        logging.error(f"Failed to parse {id_key} from link {link}: {str(e)}")
        return []


def download_document(item, base_url, library, output_dir, hudoc_type):
    """Download and save a single document."""
    doc_id = item["doc_id"]
    text = get_document_text(doc_id, base_url, library)
    if text:
        save_text(
            text,
            doc_id,
            item["title"],
            item["description"],
            output_dir,
            hudoc_type
        )
    else:
        logging.warning(f"No content retrieved for {doc_id}")


def process_rss(hudoc_type, rss_file, output_dir, full, threads):
    """Process RSS file and download documents in parallel."""
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


def process_link(hudoc_type, link, output_dir):
    """Process a single document link and download the document."""
    items = parse_link(link, hudoc_type)
    if not items:
        logging.error("No document to process")
        return

    base_url = ECHR_BASE_URL if hudoc_type == "echr" else GREVIO_BASE_URL
    item = items[0]
    doc_id = item["doc_id"]
    text = get_document_text(doc_id, base_url, LIBRARY[hudoc_type])
    if text:
        save_text(
            text,
            doc_id,
            item["title"],
            item["description"],
            output_dir,
            hudoc_type
        )
    else:
        logging.warning(f"No content retrieved for {doc_id}")
