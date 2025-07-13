import click
import logging

from .core.constants import VALID_SUBSITES
from .core.processor import process_rss


# Custom logger to use Click's colored output
class ClickHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            level = record.levelname
            if level == "DEBUG":
                click.secho(msg, fg="blue")
            elif level == "INFO":
                click.secho(msg, fg="green")
            elif level == "WARNING":
                click.secho(msg, fg="yellow")
            elif level == "ERROR":
                click.secho(msg, fg="red")
        except Exception:
            self.handleError(record)


# Configure logging with ClickHandler
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = ClickHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)


@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help=click.style(
        "Download documents from HUDOC subsites using an RSS file", fg="cyan"
    ),
    epilog=click.style(
        "Example: python -m hudoc -t echr -r rss_feed.xml -o output_dir -f -n 5",
        fg="cyan",
    ),
)
@click.option(
    "-t",
    "--type",
    type=click.Choice(VALID_SUBSITES),
    required=True,
    help=click.style("HUDOC subsite (e.g., echr, grevio, ecrml)", fg="white"),
)
@click.option(
    "-r",
    "--rss-file",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
    help=click.style("Path to RSS file", fg="white"),
)
@click.option(
    "-o",
    "--output-dir",
    default="data",
    show_default=True,
    type=click.Path(file_okay=False, writable=True),
    help=click.style("Directory to save text files (default: data)", fg="white"),
)
@click.option(
    "-f",
    "--full",
    is_flag=True,
    help=click.style("Download all documents from RSS (default: top 3)", fg="white"),
)
@click.option(
    "-n",
    "--threads",
    default=10,
    show_default=True,
    type=int,
    help=click.style(
        "Number of threads for parallel downloading (default: 10)", fg="white"
    ),
)
@click.option(
    "-d",
    "--conversion-delay",
    default=2.0,
    show_default=True,
    type=float,
    help=click.style(
        "Delay (seconds) after triggering document conversion (default: 2.0)",
        fg="white",
    ),
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help=click.style("Enable verbose logging", fg="white"),
)
@click.option(
    "-e",
    "--evid",
    is_flag=True,
    help=click.style(
        "Save output in evid format (LaTeX and YAML), for labelling.", fg="white"
    ),
)
def main(type, rss_file, output_dir, full, threads, conversion_delay, verbose, evid):
    """Download documents from HUDOC subsites using RSS file."""
    if verbose:
        logger.setLevel(logging.DEBUG)

    try:
        click.secho(f"Starting download for {type} from {rss_file}", fg="cyan")
        process_rss(
            hudoc_type=type,
            rss_file=rss_file,
            output_dir=output_dir,
            full=full,
            threads=threads,
            conversion_delay=conversion_delay,
            evid=evid,
        )
        click.secho("Document download completed", fg="green")
    except Exception as e:
        click.secho(f"An error occurred: {str(e)}", fg="red")
        raise click.ClickException(str(e))


if __name__ == "__main__":
    main()
