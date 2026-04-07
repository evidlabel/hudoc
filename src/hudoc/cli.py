import logging
import os
import sys
from pathlib import Path
from treeparse import cli, command, argument, option
from .core.processor import process_rss, process_rss_url
from .core.parser import parse_rss_file
from .core.constants import VALID_SUBSITES, SUBSITE_CONFIG

isfile = os.path.isfile


def download_callback(rss_file, output_dir="data", limit=3, threads=10, plain=False):
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
        )
        logging.info("Document download completed")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)


def list_callback(rss_file):
    """Callback for list command to display stats about the RSS file."""
    if not isfile(rss_file):
        logging.error(f"RSS file '{rss_file}' does not exist or is not a file.")
        sys.exit(1)
    subsite, items = parse_rss_file(rss_file)
    if not subsite:
        logging.error("Failed to detect subsite or parse items")
        sys.exit(1)
    if not items:
        logging.info("No items found in RSS file")
    else:
        print("Document IDs:")
        for item in items:
            print(f"- {item['doc_id']} (Title: {item['title']})")
        print(f"Subsite: {subsite}")
        print(f"Number of items: {len(items)}")


def latest_callback(subsite, output_dir, limit, threads, plain):
    """Callback for latest command."""
    url = SUBSITE_CONFIG[subsite]["rss_url"]
    logging.info(f"Fetching latest from {subsite}")
    try:
        process_rss_url(
            url=url,
            output_dir=output_dir,
            limit=limit,
            threads=threads,
            conversion_delay=2.0,
            evid=not plain,
        )
        logging.info("Download completed")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        sys.exit(1)


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
            default=10,
            help="Number of threads for parallel downloading (default: 10)",
            arg_type=int,
            sort_key=2,
        ),
        option(
            flags=["--plain", "-p"],
            default=False,
            help="Save output in plain text format (default: evid format for labelling).",
            arg_type=bool,
            sort_key=3,
        ),
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
            default=10,
            arg_type=int,
            help="Number of download threads (default: 10)",
            sort_key=3,
        ),
        option(
            flags=["--plain", "-p"],
            default=False,
            arg_type=bool,
            help="Save in plain text format (default: evid format)",
            sort_key=4,
        ),
    ],
)

app.commands.append(download_cmd)
app.commands.append(list_cmd)
app.commands.append(latest_cmd)


def main():
    app.run()


if __name__ == "__main__":
    main()
