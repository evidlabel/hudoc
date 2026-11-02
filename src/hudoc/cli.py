import logging
import sys
from pathlib import Path
from treeparse import cli, command, argument, option
from .core.processor import pdf_lines, process_rss, process_rss_url
from .core.parser import parse_rss_file
from .core.constants import VALID_SUBSITES, SUBSITE_CONFIG

DELAY = 3.0  # seconds between requests, as HUDOC asks


def download_callback(
    rss_file,
    output_dir="data",
    limit=3,
    threads=1,
    plain=False,
    delay=DELAY,
    pdf=False,
    evid_set="",
):
    """Callback for download command."""
    if not Path(rss_file).is_file():
        logging.error(f"RSS file '{rss_file}' does not exist or is not a file.")
        sys.exit(1)
    try:
        logging.info(f"Starting download from {rss_file}")
        process_rss(
            rss_file=rss_file,
            output_dir=output_dir,
            limit=limit,
            threads=threads,
            conversion_delay=2.0,
            evid=not plain,
            delay=delay,
            pdf=pdf,
            evid_set=evid_set,
        )
        if not pdf:
            logging.info("Document download completed")
    except Exception:
        logging.exception("An error occurred")
        sys.exit(1)


def list_callback(rss_file):
    """Callback for list command to display stats about the RSS file."""
    if not Path(rss_file).is_file():
        logging.error(f"RSS file '{rss_file}' does not exist or is not a file.")
        sys.exit(1)
    subsite, items = parse_rss_file(rss_file)
    if not subsite:
        logging.error("Failed to detect subsite or parse items")
        sys.exit(1)
    if not items:
        logging.info("No items found in RSS file")
    else:
        logging.info("Document IDs:")
        for item in items:
            logging.info(f"- {item['doc_id']} (Title: {item['title']})")
        logging.info(f"Subsite: {subsite}")
        logging.info(f"Number of items: {len(items)}")


def latest_callback(
    subsite, output_dir, limit, threads, plain, delay=DELAY, pdf=False, evid_set=""
):
    """Callback for latest command."""
    url = SUBSITE_CONFIG[subsite]["rss_url"]
    if limit:
        url = f"{url}&length={limit}"
    logging.info(f"Fetching latest from {subsite}")
    try:
        process_rss_url(
            url=url,
            output_dir=output_dir,
            limit=limit,
            threads=threads,
            conversion_delay=2.0,
            evid=not plain,
            delay=delay,
            pdf=pdf,
            evid_set=evid_set,
        )
        if not pdf:
            logging.info("Download completed")
    except Exception:
        logging.exception("An error occurred")
        sys.exit(1)


def pdf_callback(doc_ids, subsite="echr", evid_set=""):
    """Print the official PDF URL of each document, the version to key in evid."""
    items = [{"doc_id": d} for d in doc_ids]
    for line in pdf_lines(subsite, items, evid_set):
        print(line)


def _source_options(sort_from):
    """--delay, --pdf and --set, shared by download and latest."""
    return [
        option(
            flags=["--delay", "-d"],
            default=DELAY,
            arg_type=float,
            help="Seconds between requests (default: 3.0)",
            sort_key=sort_from,
        ),
        option(
            flags=["--pdf"],
            flag=True,
            help="Print each item's official PDF URL instead of downloading text. Key that PDF in evid; the text has no pages.",
            sort_key=sort_from + 1,
        ),
        option(
            flags=["--set"],
            dest="evid_set",
            default="",
            arg_type=str,
            help="With --pdf, print the `evid --db evid doc add -s <set>` line for each item",
            sort_key=sort_from + 2,
        ),
    ]


app = cli(
    name="hudoc",
    help="Download documents from HUDOC subsites using an RSS file.\nExample: hudoc download rss_feed.xml -o output_dir -l 5 -n 10",
    max_width=120,
    show_types=True,
    show_defaults=True,
    line_connect=True,
)

download_cmd = command(
    name="download",
    help="Download documents from HUDOC subsites using RSS file.",
    callback=download_callback,
    arguments=[
        argument(
            name="rss_file",
            arg_type=str,
            help="Path to the RSS file",
            sort_key=0,
        ),
    ],
    options=[
        option(
            flags=["--output-dir", "-o"],
            default="data",
            help="Directory to save text files (default: data)",
            arg_type=str,
            sort_key=0,
        ),
        option(
            flags=["--limit", "-l"],
            default=3,
            help="Number of documents to download (0 for all) (default: 3)",
            arg_type=int,
            sort_key=1,
        ),
        option(
            flags=["--threads", "-n"],
            default=1,
            help="Number of threads for parallel downloading (default: 1)",
            arg_type=int,
            sort_key=2,
        ),
        option(
            flags=["--plain", "-p"],
            flag=True,
            help="Save output in plain text format (default: evid format for labelling).",
            sort_key=3,
        ),
        *_source_options(4),
    ],
)

list_cmd = command(
    name="list",
    help="Display stats about the RSS file.",
    callback=list_callback,
    arguments=[
        argument(
            name="rss_file",
            arg_type=str,
            help="Path to the RSS file",
            sort_key=0,
        ),
    ],
)

latest_cmd = command(
    name="latest",
    help="Fetch and download the latest documents from a HUDOC subsite.",
    callback=latest_callback,
    options=[
        option(
            flags=["--subsite", "-s"],
            default="echr",
            arg_type=str,
            choices=VALID_SUBSITES,
            help="HUDOC subsite to fetch from (default: echr)",
            sort_key=0,
        ),
        option(
            flags=["--output-dir", "-o"],
            default="data",
            arg_type=str,
            help="Directory to save files (default: data)",
            sort_key=1,
        ),
        option(
            flags=["--limit", "-l"],
            default=3,
            arg_type=int,
            help="Number of documents to download (0 for all, default: 3)",
            sort_key=2,
        ),
        option(
            flags=["--threads", "-n"],
            default=1,
            arg_type=int,
            help="Number of download threads (default: 1)",
            sort_key=3,
        ),
        option(
            flags=["--plain", "-p"],
            flag=True,
            help="Save in plain text format (default: evid format)",
            sort_key=4,
        ),
        *_source_options(5),
    ],
)

app.commands.append(download_cmd)
app.commands.append(list_cmd)
app.commands.append(latest_cmd)

pdf_cmd = command(
    name="pdf",
    help="Print the official PDF URL of HUDOC documents by item id. Key that PDF in evid for page pinpoints.",
    callback=pdf_callback,
    arguments=[
        argument(
            name="doc_ids",
            arg_type=str,
            nargs="+",
            help="Item ids, e.g. 001-218240",
            sort_key=0,
        ),
    ],
    options=[
        option(
            flags=["--subsite", "-s"],
            default="echr",
            arg_type=str,
            choices=VALID_SUBSITES,
            help="HUDOC subsite (default: echr)",
            sort_key=0,
        ),
        option(
            flags=["--set"],
            dest="evid_set",
            default="",
            arg_type=str,
            help="Print the `evid --db evid doc add -s <set>` line instead of the bare URL",
            sort_key=1,
        ),
    ],
)
app.commands.append(pdf_cmd)


def main():
    app.run()


if __name__ == "__main__":
    main()
