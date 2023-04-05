import logging
from pathlib import Path

import click

from clean_copy import copy_files, get_gitignore_rules, get_unignored_files


@click.command()
@click.argument("source", type=click.Path(exists=True, file_okay=False))
@click.argument("destination", type=click.Path())
@click.option("--quiet", default=False, is_flag=True)
@click.option("--ignore-spec", default=".copyignore", type=str)
@click.option("--dry-run", default=False, is_flag=True)
@click.option("--include-parent-ignore", default=True, is_flag=True)
def clean_copy_cli(source, destination, quiet, ignore_spec, include_parent_ignore, dry_run):
    if quiet:
        logging.basicConfig(level=logging.ERROR)
    else:
        logging.basicConfig(level=logging.DEBUG)

    source = Path(source)
    destination = Path(destination)

    parent_rules = []
    if include_parent_ignore:
        parent_rules = get_gitignore_rules(source.parent / ".copyignore")

    unignored_files = get_unignored_files(
        root_path=source,
        folder_path=None,
        parent_rules=parent_rules,
        ignore_spec=".copyignore",
    )
    copy_count, file_size = copy_files(source, destination, unignored_files=unignored_files)
    click.echo(f"Copied {copy_count} files ({file_size} MB) from {source} to {destination}")


if __name__ == "__main__":
    clean_copy_cli()
