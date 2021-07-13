"""Provides functions for writing to file.

Functions:
    get_write_file(): Get a writeable file object.
    write_json(): Writes a python dictionary to a JSON file
"""

import json
from io import TextIOWrapper


def get_write_file(path: str) -> TextIOWrapper:
    """Given a file path, get a readable file object."""
    return open(path, 'w')


def write_json(data, file):
    """Writes a dictionary to a JSON file."""
    json.dump(data, file)
