import click
import logging

from .core.constants import VALID_SUBSITES
from .core.processor import process_rss


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Download documents from HUDOC subsites using RSS file",
)
@click.option(
    "-t",
    "--type",
    type=click.Choice(VALID_SUBSITES),
    required=True,
    help="HUDOC subsite (e.g., echr, grevio, ecrml)",
)
@click.option(
    "-r",
    "--rss-file",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help="Path to RSS file",
)
@click.option(
    "-o",
    "--output-dir",
    default="data",
    show_default=True,
    type=click.Path(file_okay=False, writable=True),
    help="Directory to save text files",
)
@click.option(
    "-f",
    "--full",
    is_flag=True,
    help="Download all documents from RSS (default: top 3)",
)
@click.option(
    "-n",
    "--threads",
    default=10,
    show_default=True,
    type=int,
    help="Number of threads for parallel downloading",
)
@click.option(
    "-d",
    "--conversion-delay",
    default=2.0,
    show_default=True,
    type=float,
    help="Delay (seconds) after triggering document conversion",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose logging",
)
@click.option(
    "-e",
    "--evid",
    is_flag=True,
    help="Save output in evid format (LaTeX and YAML) instead of plain text",
)
def main(type, rss_file, output_dir, full, threads, conversion_delay, verbose, evid):
    """Download documents from HUDOC subsites using RSS file."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        process_rss(
            hudoc_type=type,
            rss_file=rss_file,
            output_dir=output_dir,
            full=full,
            threads=threads,
            conversion_delay=conversion_delay,
            evid=evid,
        )
        logging.info("Document download completed")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
