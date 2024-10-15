from pathlib import Path
import click
from flights.airport import Airport


@click.group
def cli() -> None:
    pass


@cli.command
@click.argument("source", type=click.Path(exists=True))
@click.argument("target", nargs=-1, type=click.Path())
@click.option("--rewrite", "-f", is_flag=True, default=False)
def update_dataset(source: str, target: list[str], rewrite=bool) -> None:
    # populate_success_column(source, target)
    if len(target) > 1:
        raise click.ClickException("Too many arguments passed")
    if not target and not rewrite:
        raise click.ClickException(
            'In order to run over the input file, you must pass "--rewrite" ("-f")'
        )
    try:
        if target:
            destination: str = target[0]
        else:
            destination: str = source

        main_airport = Airport()
        main_airport.load_csv(Path(source))
        main_airport.dump_processed_csv(Path(destination))
    except Exception as reason:
        raise click.ClickException(f"Failed to update dataset: {reason}") from reason


if __name__ == "__main__":
    cli()
