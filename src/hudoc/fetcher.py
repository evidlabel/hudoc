import logging
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup

HTTP_TIMEOUT = 10  # seconds, for per-document fetches


def trigger_document_conversion(rss_link, doc_id):
    """Trigger document conversion by accessing the RSS link."""
    if not rss_link:
        logging.warning(f"No RSS link provided for {doc_id}; cannot trigger conversion")
        return False

    logging.info(f"Triggering document conversion for {doc_id} via {rss_link}")
    try:
        response = requests.get(rss_link, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        logging.debug(f"Conversion trigger successful for {doc_id}")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to trigger conversion for {doc_id}: {e!s}")
        return False


def get_document_text(doc_id, base_url, library, rss_link=None, conversion_delay=2.0):
    """Fetch document text, triggering conversion if direct download fails."""
    url = f"{base_url}?library={library}&id={urllib.parse.quote(doc_id)}"
    logging.info(f"Fetching document content for {doc_id} from {url}")

    for attempt in range(3):
        try:
            response = requests.get(url, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            for script in soup(["script", "style"]):
                script.extract()

            # Extract text from top-level text containers, avoiding nested duplicates
            text_elements = soup.find_all(["p", "li", "h1", "h2", "h3"])
            seen_texts = set()
            text_lines = []
            for element in text_elements:
                text = element.get_text(separator=" ", strip=True)
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    text_lines.append(text)

            # Join paragraphs with double newlines for readability
            text = "\n\n".join(text_lines)
            if text.strip():
                return text
            logging.warning(f"Empty content for {doc_id} on attempt {attempt + 1}")
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed for {doc_id}: {e!s}")

        # If direct download failed or content is empty, try triggering conversion
        if rss_link and attempt < 2:
            if trigger_document_conversion(rss_link, doc_id):
                logging.info(f"Waiting {conversion_delay}s for conversion of {doc_id}")
                time.sleep(conversion_delay)
            else:
                logging.warning(
                    f"Conversion trigger failed for {doc_id}; retrying direct download"
                )
        elif attempt == 2:
            logging.error(f"Failed to fetch content for {doc_id} after 3 attempts")
            return None

    return None
