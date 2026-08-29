import logging
import os
from pathlib import Path

from .evid import save_evid


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
            logging.error(f"Failed to save file for {doc_id}: {e!s}")
