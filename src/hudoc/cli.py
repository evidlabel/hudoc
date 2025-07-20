import rich_click as click
import logging

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
        "Example: python -m hudoc rss_feed.xml -o output_dir -l 5 -n 10",
        fg="cyan",
    ),
)
@click.argument(
    "rss_file",
    type=click.Path(exists=True, dir_okay=False),
    required=True,
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
    "-l",
    "--limit",
    default=3,
    show_default=True,
    type=int,
    help=click.style("Number of documents to download (0 for all)", fg="white"),
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
    "-p",
    "--plain",
    is_flag=True,
    help=click.style(
        "Save output in plain text format (default: evid format for labelling).",
        fg="white",
    ),
)
def main(rss_file, output_dir, limit, threads, plain):
    """Download documents from HUDOC subsites using RSS file."""
    try:
        click.secho(f"Starting download from {rss_file}", fg="cyan")
        process_rss(
            rss_file=rss_file,
            output_dir=output_dir,
            limit=limit,
            threads=threads,
            conversion_delay=2.0,
            evid=not plain,
        )
        click.secho("Document download completed", fg="green")
    except Exception as e:
        click.secho(f"An error occurred: {str(e)}", fg="red")
        raise click.ClickException(str(e))

if __name__ == "__main__":
    main()
