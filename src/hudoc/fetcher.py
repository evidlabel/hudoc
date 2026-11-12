import logging
import os
import shutil
import subprocess
import tempfile
import time
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup

HTTP_TIMEOUT = 10  # seconds, for per-document text fetches
PDF_TIMEOUT = 60  # seconds, a judgment PDF can be several MB
PDF_TRAILER_WINDOW = 1024  # bytes searched for the %%EOF trailer


@dataclass
class Response:
    """What ``http_get`` got back. ``status`` 0 means curl itself failed."""

    status: int
    content: bytes = b""
    error: str = ""

    @property
    def ok(self):
        return 200 <= self.status < 300

    @property
    def text(self):
        return self.content.decode("utf-8", errors="replace")

    def reason(self):
        return self.error or f"HTTP {self.status}"


def http_get(url, timeout=HTTP_TIMEOUT):
    """GET ``url`` with the curl binary, with curl's own default headers.

    HUDOC sits behind Cloudflare, which answers python-requests with a 403
    JavaScript challenge but serves curl. So every HUDOC fetch goes through here.
    """
    curl = shutil.which("curl")
    if not curl:
        return Response(0, error="curl not found on PATH")
    with tempfile.TemporaryDirectory() as tmp:
        body = Path(tmp) / "body"
        cmd = [curl, "-sS", "-L", "--max-time", str(timeout)]
        cmd += ["-o", str(body), "-w", "%{http_code}", url]
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout + 5
            )
        except subprocess.TimeoutExpired:
            return Response(0, error=f"timed out after {timeout}s")
        if proc.returncode:
            return Response(0, error=proc.stderr.strip() or f"curl exit {proc.returncode}")
        code = proc.stdout.strip()
        content = body.read_bytes() if body.exists() else b""
    return Response(int(code) if code.isdigit() else 0, content)


def trigger_document_conversion(rss_link, doc_id):
    """Trigger document conversion by accessing the RSS link."""
    if not rss_link:
        logging.warning(f"No RSS link provided for {doc_id}; cannot trigger conversion")
        return False

    logging.info(f"Triggering document conversion for {doc_id} via {rss_link}")
    response = http_get(rss_link)
    if response.ok:
        logging.debug(f"Conversion trigger successful for {doc_id}")
        return True
    logging.error(f"Failed to trigger conversion for {doc_id}: {response.reason()}")
    return False


# Block-level text containers, in the order a judgment uses them.
_BLOCK_TAGS = ("p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre")


def _element_text(element):
    return element.get_text(separator=" ", strip=True)


def _table_row_text(row):
    """One table row as a single line: ``Application No. | 12345/20``."""
    cells = [
        _element_text(cell) for cell in row.find_all(["th", "td"], recursive=False)
    ]
    return " | ".join(cell for cell in cells if cell)


def _page_text(html):
    """The page's text in document order, with tables kept as row lines.

    Duplicates are suppressed by *node identity* (an element already emitted
    through an ancestor or a table row), never by string equality: a judgment
    legitimately repeats headings, section labels and boilerplate paragraphs,
    and dropping the later copies silently breaks the verbatim contract.
    """
    soup = BeautifulSoup(html, "html.parser")
    for script in soup(["script", "style"]):
        script.extract()

    text_lines = []
    seen_nodes = set()

    def emit(element, text):
        if not text or id(element) in seen_nodes:
            return
        seen_nodes.add(id(element))
        text_lines.append(text)

    for element in soup.find_all(list(_BLOCK_TAGS) + ["tr", "div"]):
        if id(element) in seen_nodes:
            continue
        if element.name == "tr":
            # A row is emitted whole; its cells are skipped as table descendants.
            emit(element, _table_row_text(element))
            continue
        if element.find_parent("table") is not None:
            continue
        if element.name == "div":
            # Fallback for text that sits in bare <div>s: only emit a div that
            # does not contain other extractable blocks (no double capture).
            if element.find(list(_BLOCK_TAGS) + ["div", "table"]) is not None:
                continue
        elif element.find_parent(_BLOCK_TAGS) is not None:
            continue
        emit(element, _element_text(element))

    # Join paragraphs with double newlines for readability
    return "\n\n".join(text_lines)


def get_document_text(doc_id, base_url, library, rss_link=None, conversion_delay=2.0):
    """Fetch document text, triggering conversion if direct download fails."""
    url = f"{base_url}?library={library}&id={urllib.parse.quote(doc_id)}"
    logging.info(f"Fetching document content for {doc_id} from {url}")

    for attempt in range(3):
        response = http_get(url)
        if response.ok:
            text = _page_text(response.text)
            if text.strip():
                return text
            logging.warning(f"Empty content for {doc_id} on attempt {attempt + 1}")
        else:
            logging.warning(
                f"Attempt {attempt + 1} failed for {doc_id}: {response.reason()}"
            )

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


def _has_pdf_trailer(content, window=PDF_TRAILER_WINDOW):
    """A real PDF ends with ``%%EOF``; a proxy fragment or interrupted body does not."""
    return b"%%EOF" in content[-window:]


def is_complete_pdf(path, window=PDF_TRAILER_WINDOW):
    """True when ``path`` holds a whole PDF: a ``%PDF`` header and a ``%%EOF`` trailer.

    Only the head and the last kilobyte are read — a judgment PDF can be several
    MB and this runs once per item on every run.
    """
    try:
        with open(path, "rb") as handle:
            if not handle.read(5).startswith(b"%PDF"):
                return False
            handle.seek(0, os.SEEK_END)
            handle.seek(max(handle.tell() - window, 0))
            return b"%%EOF" in handle.read()
    except OSError:
        return False


def get_document_pdf(url, path, timeout=PDF_TIMEOUT):
    """Save the PDF at ``url`` to ``path``; return ``path``, or None on failure.

    Refuses any body that does not start with ``%PDF``, such as a challenge page,
    and any body without a ``%%EOF`` trailer, which is a truncated download.
    HUDOC answers 204 with no body for an item id it does not have.

    The body is written beside the target and renamed with ``os.replace``, so an
    interrupted write can never leave a short file at ``path``.
    """
    response = http_get(url, timeout)
    if response.status == 204:
        logging.error(f"HUDOC has no document at {url} (204); check the item id")
    elif not response.ok:
        logging.error(f"Failed to fetch {url}: {response.reason()}")
    elif not response.content.startswith(b"%PDF"):
        logging.error(f"Not a PDF from {url}: {response.content[:60]!r}")
    elif not _has_pdf_trailer(response.content):
        logging.error(
            f"Truncated PDF from {url}: {len(response.content)} bytes without a "
            f"%%EOF trailer; not saving"
        )
    else:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f"{path.name}.part")
        try:
            with open(tmp, "wb") as handle:
                handle.write(response.content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, path)
        except OSError as e:
            logging.error(f"Failed to save {path}: {e!s}")
            try:
                tmp.unlink()
            except OSError:
                pass
            return None
        return path
    return None
