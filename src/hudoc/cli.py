import logging
import sys
from pathlib import Path

# Add treeparse to sys.path
sys.path.append(
    str(Path(__file__).resolve().parent.parent.parent / ".." / "treeparse" / "src")
)

from treeparse import cli, command, argument, option

from .core.processor import process_rss


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

app.commands.append(download_cmd)


def main():
    app.run()


if __name__ == "__main__":
    main()
