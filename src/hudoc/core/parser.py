import json
import logging
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from .constants import SUBSITE_CONFIG


def parse_rss_file(rss_file, hudoc_type):
    try:
        tree = ET.parse(rss_file)
        root = tree.getroot()
        items = []
        id_key = SUBSITE_CONFIG[hudoc_type]["id_key"]
        for item in root.findall(".//item"):
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
                    logging.warning(
                        f"Failed to parse pubDate {pub_date_elem.text}: {str(e)}"
                    )

            try:
                fragment = link.split("#")[1]
                fragment = urllib.parse.unquote(fragment)
                data = json.loads(fragment)
                doc_id = data[id_key][0]
                items.append(
                    {
                        "doc_id": doc_id,
                        "title": title,
                        "description": description,
                        "verdict_date": verdict_date,
                        "rss_link": link,
                    }
                )
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
