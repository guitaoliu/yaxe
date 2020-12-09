import json
from pathlib import Path
from typing import Dict

from rich import print

config_example = {"WEB": {"PUBLIC_KEY": "0725@pwdorgopenp"}, "USER": {}}
CONFIG_FILE = "config.json"


def load_config() -> Dict:
    config_file = Path(CONFIG_FILE)
    if not config_file.exists():
        print("No config file detected using default config instead.")
        print("please input your netid: ", end="")
        netid = input().strip()
        print("Please input your password: ", end="")
        password = input().strip()
        config_example["USER"]["NETID"] = netid
        config_example["USER"]["PASSWORD"] = password
        with open(CONFIG_FILE, "w", encoding="utf8") as f:
            json.dump(config_example, f)
        return config_example
    else:
        return json.loads(config_file.read_text())


class Config:
    def __init__(self) -> None:
        config = load_config()

        self.net_id = config["USER"]["NETID"]
        self.password = config["USER"]["PASSWORD"]
        self.public_key = config["WEB"]["PUBLIC_KEY"]


config = Config()
