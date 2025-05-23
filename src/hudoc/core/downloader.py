import logging

from ..utils import get_document_text, save_text

ECHR_BASE_URL = "https://hudoc.echr.coe.int/app/conversion/docx/html/body"
GREVIO_BASE_URL = "https://hudoc.grevio.coe.int/app/conversion/docx/html/body"
LIBRARY = {"echr": "ECHR", "grevio": "GREVIO"}


def download_document(item, base_url, library, output_dir, hudoc_type, evid=False):
    doc_id = item["doc_id"]
    text = get_document_text(doc_id, base_url, library)
    if text:
        save_text(
            text,
            doc_id,
            item["title"],
            item["description"],
            output_dir,
            hudoc_type,
            verdict_date=item.get("verdict_date"),
            evid=evid,
        )
    else:
        logging.warning(f"No content retrieved for {doc_id}")
