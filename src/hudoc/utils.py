"""Compatibility facade: re-export split util modules for existing imports."""

from .evid import clean_text_for_typst, save_evid, typst_dict
from .fetcher import HTTP_TIMEOUT, get_document_text, trigger_document_conversion
from .writer import save_text

__all__ = [
    "HTTP_TIMEOUT",
    "clean_text_for_typst",
    "get_document_text",
    "save_evid",
    "save_text",
    "trigger_document_conversion",
    "typst_dict",
]
