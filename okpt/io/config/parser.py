from io import TextIOWrapper
import json
from typing import Any, Dict

import yaml
from okpt.io import reader


def parse_yaml(file: TextIOWrapper) -> Dict[str, Any]:
    return yaml.load(file, Loader=yaml.SafeLoader)


def parse_yaml_from_path(path: str):
    file = reader.get_read_file_obj(path)
    return parse_yaml(file)


def parse_json(file: TextIOWrapper) -> Dict[str, Any]:
    return json.load(file)


def parse_json_from_path(path: str):
    file = reader.get_read_file_obj(path)
    return json.load(file)
