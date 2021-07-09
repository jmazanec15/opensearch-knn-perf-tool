import json
import yaml


def parse_yaml(file):
    return yaml.load(file, Loader=yaml.SafeLoader)


def parse_json(file):
    return json.load(file)
