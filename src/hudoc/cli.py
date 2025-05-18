import argparse
import logging

from .core.processor import process_rss, process_link, process_rss_link

def main():
    """Parse CLI arguments and run the HUDOC document downloader."""
    parser = argparse.ArgumentParser(
        description="Download ECHR or GREVIO HUDOC documents from RSS feed or link",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--type",
        choices=["echr", "grevio"],
        required=True,
        help="HUDOC type (echr or grevio)"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--rss-file",
        help="Path to RSS file"
    )
    input_group.add_argument(
        "--link",
        help="Single document URL (e.g., http://hudoc.echr.coe.int/eng#{\"itemid\":[\"001-243083\"]}) or RSS feed URL"
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory to save text files"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Download all documents from RSS (default: top 3)"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=10,
        help="Number of threads for parallel downloading (RSS only)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        if args.rss_file:
            process_rss(
                hudoc_type=args.type,
                rss_file=args.rss_file,
                output_dir=args.output_dir,
                full=args.full,
                threads=args.threads
            )
        elif "/app/transform/rss" in args.link:
            process_rss_link(
                hudoc_type=args.type,
                link=args.link,
                output_dir=args.output_dir,
                full=args.full,
                threads=args.threads
            )
        else:
            process_link(
                hudoc_type=args.type,
                link=args.link,
                output_dir=args.output_dir
            )
        logging.info("Document download completed")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
