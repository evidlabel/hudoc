import logging
import xml.etree.ElementTree as ET
import json
import urllib.parse

def parse_rss_file(rss_file, hudoc_type):
    """Parse RSS file and extract document IDs, titles, and descriptions.

    Args:
        rss_file (str): Path to the RSS file.
        hudoc_type (str): Type of HUDOC database ('echr' or 'grevio').

    Returnssoft: Returns:
        list: List of dicts with doc_id, title, and description.
    """
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
    """Parse a single document link to extract doc_id, with dummy title and description.

    Args:
        link (str): URL of the document.
        hudoc_type (str): Type of HUDOC database ('echr' or 'grevio').

    Returns:
        list: List with one dict containing doc_id, title, and description.
    """
    id_key = "itemid" if hudoc_type == "echr" else "greviosectionid"
    try:
        fragment = link.split("#", 1)[1]
        fragment = urllib.parse.unquote(fragment)
        # Normalize JSON by replacing single quotes with double quotes
        fragment = fragment.replace("'", "\"")
        data = json.loads(fragment)
        doc_id = data[id_key][0] if isinstance(data[id_key], list) else data[id_key]
        return [{"doc_id": doc_id, "title": "Untitled", "description": "No description"}]
    except (IndexError, json.JSONDecodeError, KeyError) as e:
        logging.error(f"Failed to parse {id_key} from link {link}: {str(e)}. Expected a document URL with a #{id_key} fragment.")
        return []
