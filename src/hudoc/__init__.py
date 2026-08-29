import logging

from .cli import main

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

__all__ = ["main"]
