"""Provides functions for writing to file.

Functions:
    write_json(): Writes a python dictionary to a JSON file
"""

import json


def write_json(data, file):
    """Writes a dictionary to a JSON file.

    Args:
        data: A dictionary to be converted to JSON.
        file: Path of output file.
    """

    json.dump(data, file)
