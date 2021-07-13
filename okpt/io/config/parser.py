# SPDX-License-Identifier: Apache-2.0

# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

# Modifications Copyright OpenSearch Contributors. See
# GitHub history for details.
"""Provides methods to parse YAML and JSON files."""

import json
from io import TextIOWrapper
from typing import Any, Dict

import yaml

from okpt.io import reader


def parse_yaml(file: TextIOWrapper) -> Dict[str, Any]:
    """Parses YAML file from file object."""
    return yaml.load(file, Loader=yaml.SafeLoader)


def parse_yaml_from_path(path: str):
    """Parses YAML file from file path."""
    file = reader.get_read_file_obj(path)
    return parse_yaml(file)


def parse_json(file: TextIOWrapper) -> Dict[str, Any]:
    """Parses JSON file from file object."""
    return json.load(file)


def parse_json_from_path(path: str):
    """Parses JSON file from file path."""
    file = reader.get_read_file_obj(path)
    return json.load(file)
