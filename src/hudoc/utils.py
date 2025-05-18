import logging
import os
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def get_document_text(doc_id, base_url, library):
    """Fetch and extract plain text from a HUDOC document.

    Args:
        doc_id (str): Document ID (itemid for ECHR, greviosectionid for GREVIO).
        base_url (str): Base URL for the HUDOC API.
        library (str): Library name (ECHR or GREVIO).

    Returns:
        str: Extracted text, or None if failed.

    """
    url = f"{base_url}?library={library}&id={urllib.parse.quote(doc_id)}"
    logging.info(f"Fetching document content for {doc_id} from {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch content for {doc_id}: {str(e)}")
        return None

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
    return text if text.strip() else None


def save_text(text, doc_id, title, description, output_dir, hudoc_type):
    """Save the text to a file in the output directory.

    Args:
        text (str): Document text to save.
        doc_id (str): Document ID.
        title (str): Document title.
        description (str): Document description (GREVIO only).
        output_dir (str): Directory to save the file.
        hudoc_type (str): Type of HUDOC database ('echr' or 'grevio').

    """
    prefix = "echr_case" if hudoc_type == "echr" else "grevio_doc"
    safe_id = doc_id.replace("/", "_").replace(":", "_").replace(" ", "_")
    filename = f"{prefix}_{safe_id}.txt"
    filepath = os.path.join(output_dir, filename)

    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Title: {title}\n")
            if description and hudoc_type == "grevio":
                f.write(f"Description: {description}\n\n")
            f.write(text)
        logging.info(f"Saved content for {doc_id} to {filepath}")
    except OSError as e:
        logging.error(f"Failed to save file for {doc_id}: {str(e)}")
