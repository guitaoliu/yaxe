# yaxe

Yaxe helps you use the Xi'an Jiaotong University grade system efficiently with some enhanced features.

[![asciicast](https://asciinema.org/a/qMO4QrMbP7O57u5z5G4i9rTK2.svg)](https://asciinema.org/a/qMO4QrMbP7O57u5z5G4i9rTK2)

## Install

```shell
git clone https://github.com/guitaoliu/yaxe.git
pipenv install
```

## Usage

```shell
python -m yaxe grade
python -m yaxe gpa
```

This project is using [click](https://click.palletsprojects.com/en/7.x/). Check info with `python -m yaxe --help`

```shell
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  gpa    Calculate your gpa using the grade file.
  grade  Fetching your grade from ehall website.
```

## Passwords

Your netid and corresponding password will only be stored on your machine in `config.json`. Please remove it at the appropriate time.

## Credits

- The origin version was built by [@chaoers](https://github.com/chaoers).
