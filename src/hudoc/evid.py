import logging
import os
import re
import textwrap
import uuid
from datetime import datetime
from pathlib import Path
from string import Template

import yaml

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
            items = ", ".join(f'"{item.replace('"', '\\"')}"' for item in v)
            parts.append(f"{k}: ({items})")
        else:
            parts.append(f"{k}: {v}")
    return "(" + ", ".join(parts) + ")"


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
        tags=["hudoc", hudoc_type],
        time_added=datetime.now().strftime("%Y-%m-%d"),
        title=title or "Untitled",
        url=f'https://hudoc.{hudoc_type}.coe.int/eng#{{"{id_key}":["{doc_id}"]}}',
        uuid=subdir,
    )
    yaml_content = metadata.model_dump()

    # Create dict for Typst mset with overrides
    mset_dict = yaml_content.copy()
    mset_dict["date"] = date
    mset_dict["title"] = description
    mset_str = typst_dict(mset_dict)

    template = r"""#import "@local/labtyp:0.1.0": lablist, lab, mset

#mset(values: $mset_str)

#outline()

= $safe_id

$cleaned_text

= List of Labels
#lablist()
"""

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
        logging.error(f"Failed to save evid files for {doc_id}: {e!s}")
