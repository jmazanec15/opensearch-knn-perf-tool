# SPDX-License-Identifier: Apache-2.0

# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

# Modifications Copyright OpenSearch Contributors. See
# GitHub history for details.
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
