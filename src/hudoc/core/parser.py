import json
import logging
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from .constants import SUBSITE_CONFIG, VALID_SUBSITES

def parse_rss_file(rss_file):
    """Parse RSS file and detect subsite from URLs."""
    try:
        tree = ET.parse(rss_file)
        root = tree.getroot()
        items = root.findall(".//item")
        if not items:
            logging.warning("No items found in RSS file")
            return None, []  # subsite, items

        # Detect subsite from the first item's link
        first_link = items[0].find("link").text
        if first_link:
            # Extract subsite from URL, e.g., 'echr' from 'hudoc.echr.coe.int'
            parsed_url = urllib.parse.urlparse(first_link)
            host_parts = parsed_url.hostname.split('.')
            if len(host_parts) >= 3 and host_parts[1] in VALID_SUBSITES:
                subsite = host_parts[1]  # e.g., 'echr'
            else:
                raise ValueError(f"Invalid or unrecognized subsite in URL: {first_link}")
            id_key = SUBSITE_CONFIG[subsite]["id_key"]
        else:
            raise ValueError("First item has no link to detect subsite")

        parsed_items = []
        for item in items:
            link = item.find("link").text
            title = item.find("title").text or "Untitled"
            description = item.find("description").text or "No description"
            pub_date_elem = item.find("pubDate")
            verdict_date = None
            if pub_date_elem is not None and pub_date_elem.text:
                try:
                    pub_date = parsedate_to_datetime(pub_date_elem.text)
                    verdict_date = pub_date.strftime("%Y-%m-%d")
                except (ValueError, TypeError) as e:
                    logging.warning(f"Failed to parse pubDate: {str(e)}")

            try:
                fragment = link.split("#")[1]
                fragment = urllib.parse.unquote(fragment)
                data = json.loads(fragment)
                doc_id = data.get(id_key, [None])[0]  # Use detected id_key
                if doc_id:
                    parsed_items.append({
                        "doc_id": doc_id,
                        "title": title,
                        "description": description,
                        "verdict_date": verdict_date,
                        "rss_link": link,
                    })
            except (IndexError, json.JSONDecodeError, KeyError, ValueError) as e:
                logging.warning(f"Failed to parse item from link {link}: {str(e)}")
                continue

        logging.info(f"Parsed {len(parsed_items)} items from RSS file for subsite {subsite}")
        return subsite, parsed_items
    except ET.ParseError as e:
        logging.error(f"Failed to parse RSS file: {str(e)}")
        return None, []
    except FileNotFoundError:
        logging.error(f"RSS file not found: {rss_file}")
        return None, []
    except Exception as e:
        logging.error(f"Error parsing RSS file: {str(e)}")
        return None, []
