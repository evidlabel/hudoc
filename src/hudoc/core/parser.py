import json
import logging
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
import requests
from .constants import SUBSITE_CONFIG, VALID_SUBSITES


def _doc_id_from_link(link, id_key):
    """Extract a document id from a HUDOC item URL.

    Saved portal RSS uses a JSON fragment (`#{"itemid":["…"]}`). Live
    transform/rss feeds use `?i=<doc_id>`.
    """
    parsed = urllib.parse.urlparse(link)
    if parsed.fragment:
        fragment = urllib.parse.unquote(parsed.fragment)
        data = json.loads(fragment)
        return data.get(id_key, [None])[0]
    ids = urllib.parse.parse_qs(parsed.query).get("i")
    if ids:
        return ids[0]
    raise ValueError(f"No document id in link: {link}")


def _parse_items(root, source_kind):
    """Detect subsite from items and return (subsite, parsed_items).

    source_kind is the word "file" or "feed" used in log messages.
    """
    items = root.findall(".//item")
    if not items:
        logging.warning(f"No items found in RSS {source_kind}")
        return None, []

    link_elem = items[0].find("link")
    first_link = link_elem.text if link_elem is not None else None
    if first_link:
        parsed_url = urllib.parse.urlparse(first_link)
        host_parts = parsed_url.hostname.split(".")
        if len(host_parts) >= 3 and host_parts[1] in VALID_SUBSITES:
            subsite = host_parts[1]
        else:
            raise ValueError(f"Invalid or unrecognized subsite in URL: {first_link}")
        id_key = SUBSITE_CONFIG[subsite]["id_key"]
    else:
        raise ValueError("First item has no link to detect subsite")

    parsed_items = []
    for item in items:
        link_elem = item.find("link")
        link = link_elem.text if link_elem is not None else None
        if not link:
            logging.warning("Item has no link; skipping")
            continue

        title_elem = item.find("title")
        title = title_elem.text if title_elem is not None else "Untitled"

        description_elem = item.find("description")
        description = (
            description_elem.text if description_elem is not None else "No description"
        )

        pub_date_elem = item.find("pubDate")
        verdict_date = None
        if pub_date_elem is not None and pub_date_elem.text:
            try:
                pub_date = parsedate_to_datetime(pub_date_elem.text)
                verdict_date = pub_date.strftime("%Y-%m-%d")
            except (ValueError, TypeError) as e:
                logging.warning(f"Failed to parse pubDate: {e!s}")

        try:
            doc_id = _doc_id_from_link(link, id_key)
            if doc_id:
                parsed_items.append(
                    {
                        "doc_id": doc_id,
                        "title": title,
                        "description": description,
                        "verdict_date": verdict_date,
                        "rss_link": link,
                    }
                )
        except (IndexError, json.JSONDecodeError, KeyError, ValueError) as e:
            logging.warning(f"Failed to parse item from link {link}: {e!s}")
            continue

    logging.info(
        f"Parsed {len(parsed_items)} items from RSS {source_kind} for subsite {subsite}"
    )
    return subsite, parsed_items


def parse_rss_file(rss_file):
    """Parse RSS file and detect subsite from URLs."""
    try:
        tree = ET.parse(rss_file)
        return _parse_items(tree.getroot(), "file")
    except ET.ParseError as e:
        logging.error(f"Failed to parse RSS file: {e!s}")
        return None, []
    except FileNotFoundError:
        logging.error(f"RSS file not found: {rss_file}")
        return None, []
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing RSS file: {e!s}")
        return None, []


def parse_rss_url(url):
    """Fetch RSS from a URL and detect subsite from item links."""
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        return _parse_items(root, "feed")
    except requests.RequestException as e:
        logging.error(f"Failed to fetch RSS from {url}: {e!s}")
        return None, []
    except ET.ParseError as e:
        logging.error(f"Failed to parse RSS from {url}: {e!s}")
        return None, []
    except (ValueError, KeyError) as e:
        logging.error(f"Error fetching RSS from {url}: {e!s}")
        return None, []
