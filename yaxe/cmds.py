from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from yaxe.grade import GPACalculator, GradeParser

console = Console()


@click.group()
def cli():
    pass


@click.command(name="grade", help="Fetching your grade from ehall website.")
@click.option(
    "--force", default=False, is_flag=True, help="Force update local grade data."
)
@click.option(
    "--print", default=False, is_flag=True, help="Print GPA result after grade updated."
)
def fetch_grade(force, print):
    output_file = Path("result")
    parser = GradeParser()
    if not output_file.exists():
        output_file.mkdir()
    if force:
        parser.save()
    else:
        if output_file.joinpath("grade.csv").exists():
            console.print(
                "[red]Grade file already exist, setting force flag to update file!"
            )
        else:
            parser.save()
            console.print("[red]Success updated grade!")


@click.command(name="gpa", help="Calculate your gpa using the grade file.")
def get_gpa():
    data_file = Path("result")
    if data_file.exists():
        res = GPACalculator()
        table = Table(title="GAP result")
        table.add_column("Method", style="cyan")
        table.add_column("Result")

        for method, gpa in res.get_gpa().items():
            table.add_row(method, str(round(gpa, 2)))
        console.print(table)
    else:
        print("[red]Please run grade fetch first!")


cli.add_command(fetch_grade)
cli.add_command(get_gpa)
