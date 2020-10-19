from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from core.grade import GradeParser, GPACalculator

console = Console()


@click.group()
def cli():
    pass


@click.command(help='fetch grades')
@click.option('--update', default=False, is_flag=True, help='force update the grade file')
@click.option('--output', default='result/grade.csv', help='grade file output dir')
def fetch_grade(update, output):
    output_file = Path(output)
    if not output_file.parent.exists():
        output_file.parent.mkdir()

    if output_file.exists() and not update:
        console.print(
            '[red]Grade file already exist, setting update to true to update the file!')

    if update or not output_file.exists():
        grade = GradeParser()
        grade.save_csv(output_file)
        print('Fetching...')
        print('Done...')


@click.command(help='calculate your gpa using the grade file')
@click.option('--data-file', default='result/grade.csv', help='grade file dir')
def get_gpa(data_file):
    data_file = Path(data_file)
    if data_file.exists():
        res = GPACalculator(data_file)
        table = Table(title='GAP result')
        table.add_column('Method', style='cyan')
        table.add_column('Result')

        for method, gpa in res.get_gpa().items():
            table.add_row(
                method, str(round(gpa, 2))
            )
        console.print(table)
    else:
        print('[red]Please run grade fetch first!')


cli.add_command(fetch_grade)
cli.add_command(get_gpa)


if __name__ == "__main__":
    cli()
