import logging
import os
import textwrap
import time
import urllib.parse
import uuid
from datetime import datetime
from pathlib import Path
from string import Template

import requests
import yaml
from bs4 import BeautifulSoup
import re

from .core.constants import SUBSITE_CONFIG
from .models import EvidMetadata


def clean_text_for_typst(text: str) -> str:
    """Clean text for Typst by escaping special characters and normalizing newlines."""
    text = re.sub(r"(\n\s*\n)+", r"\n\n", text)
    escapes = {
        "\\": "\\\\",
        "#": "\\#",
        "*": "\\*",
        "_": "\\_",
        "~": "\\~",
        "^": "\\^",
        "`": "\\`",
        '"': '\\"',
        "$": "\\$",
        "<": "\\<",
        ">": "\\>",
    }
    return "".join(escapes.get(c, c) for c in text)


def typst_dict(d: dict) -> str:
    """Convert Python dict to Typst dict string."""
    parts = []
    for k, v in d.items():
        if isinstance(v, str):
            escaped_v = v.replace('"', '\\"')
            parts.append(f'{k}: "{escaped_v}"')
        elif isinstance(v, list):
            items = ", ".join(f'"{item.replace("\"", "\\\"")}"' for item in v)
            parts.append(f"{k}: ({items})")
        else:
            parts.append(f"{k}: {v}")
    return "(" + ", ".join(parts) + ")"


def trigger_document_conversion(rss_link, doc_id):
    """Trigger document conversion by accessing the RSS link."""
    if not rss_link:
        logging.warning(f"No RSS link provided for {doc_id}; cannot trigger conversion")
        return False

    logging.info(f"Triggering document conversion for {doc_id} via {rss_link}")
    try:
        response = requests.get(rss_link, timeout=10)
        response.raise_for_status()
        logging.debug(f"Conversion trigger successful for {doc_id}")
        return True
    except requests.RequestException as e:
        logging.error(f"Failed to trigger conversion for {doc_id}: {str(e)}")
        return False


def get_document_text(doc_id, base_url, library, rss_link=None, conversion_delay=2.0):
    """Fetch document text, triggering conversion if direct download fails."""
    url = f"{base_url}?library={library}&id={urllib.parse.quote(doc_id)}"
    logging.info(f"Fetching document content for {doc_id} from {url}")

    for attempt in range(3):
        try:
            response = requests.get(url, timeout=10)
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
            logging.warning(f"Attempt {attempt + 1} failed for {doc_id}: {str(e)}")

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


def save_text(
    text,
    doc_id,
    title,
    description,
    output_dir,
    hudoc_type,
    verdict_date=None,
    evid=False,
):
    """Save document text in plain text or evid format."""
    prefix = f"{hudoc_type}_doc"
    safe_id = doc_id.replace("/", "_").replace(":", "_").replace(" ", "_")
    filename = f"{prefix}_{safe_id}.txt"

    if evid:
        save_evid(
            text,
            doc_id,
            title,
            description,
            output_dir,
            hudoc_type,
            filename,
            verdict_date,
        )
    else:
        filepath = os.path.join(output_dir, filename)
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Title: {title}\n")
                if description:
                    f.write(f"Description: {description}\n\n")
                f.write(text)
            logging.info(f"Saved content for {doc_id} to {filepath}")
        except OSError as e:
            logging.error(f"Failed to save file for {doc_id}: {str(e)}")


def save_evid(
    text,
    doc_id,
    title,
    description,
    output_dir,
    hudoc_type,
    filename,
    verdict_date=None,
):
    """Save document in evid format with Typst and YAML files."""
    unique_name = f"{hudoc_type}_{doc_id}"
    subdir = str(uuid.uuid5(uuid.NAMESPACE_URL, unique_name))
    subdir_path = os.path.join(output_dir, subdir)
    typst_file = os.path.join(subdir_path, "label.typ")
    yaml_file = os.path.join(subdir_path, "info.yml")
    safe_id = doc_id.replace("/", "_").replace(":", "_").replace(" ", "_")

    # Check if complete files already exist
    if Path(subdir_path).exists():
        typst_path = Path(typst_file)
        yaml_path = Path(yaml_file)
        if typst_path.exists() and yaml_path.exists():
            logging.info(
                f"Evid format for {doc_id} already exists at {subdir_path}, skipping"
            )
            return
        else:
            logging.warning(
                f"Partial evid files found for {doc_id} at {subdir_path}, overwriting"
            )

    # Clean text for Typst
    cleaned_text = clean_text_for_typst(text)

    # Create YAML metadata
    id_key = SUBSITE_CONFIG[hudoc_type]["id_key"]
    date = verdict_date or datetime.now().strftime("%Y-%m-%d")

    metadata = EvidMetadata(
        authors=hudoc_type,
        dates=date,
        label=description or "No description",
        original_name=filename,
        tags=["hudoc"] + [hudoc_type],
        time_added=datetime.now().strftime("%Y-%m-%d"),
        title=title or "Untitled",
        url=f'https://hudoc.{hudoc_type}.coe.int/eng#{{"{id_key}":["{doc_id}"]}}',
        uuid=subdir,
    )
    yaml_content = metadata.model_dump()

    # Create Typst content with metadata in mset

    yaml_content["date"] = date
    yaml_content["title"] = description

    mset_str = typst_dict(yaml_content)
    template = r"""#import "@local/labtyp:0.1.0": lablist, lab, mset

#mset(values: $mset_str)

#outline()

= $safe_id

$cleaned_text

= List of Labels
#lablist()
"""
    mset_str

    typst_content = Template(textwrap.dedent(template)).substitute(
        mset_str=mset_str, safe_id=safe_id, cleaned_text=cleaned_text
    )

    try:
        Path(subdir_path).mkdir(parents=True, exist_ok=True)
        with open(typst_file, "w", encoding="utf-8") as f:
            f.write(typst_content)
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(yaml_content, f, allow_unicode=True, default_style="'")
        logging.info(f"Saved evid format for {doc_id} to {subdir_path}")
    except OSError as e:
        logging.error(f"Failed to save evid files for {doc_id}: {str(e)}")
