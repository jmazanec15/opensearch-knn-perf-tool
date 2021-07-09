from io import TextIOWrapper
import json
from typing import Any, Dict

import yaml


def parse_yaml(file: TextIOWrapper) -> Dict[Any, Any]:
    return yaml.load(file, Loader=yaml.SafeLoader)


def parse_json(file: TextIOWrapper) -> Dict[Any, Any]:
    return json.load(file)
