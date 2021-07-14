# SPDX-License-Identifier: Apache-2.0

# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

# Modifications Copyright OpenSearch Contributors. See
# GitHub history for details.
"""Parses and defines command line arguments for the program.

Defines the subcommands `test`, `plot`, and `compare` and the corresponding
files that are required by each command.

Functions:
    get_read_file_obj(): Get a readable file object.
    define_args(): Define the command line arguments.
    get_args(): Returns a dictionary of the command line args.
"""

import argparse
from io import TextIOWrapper
from typing import Dict, Any

_readable_file_type = argparse.FileType('r')
_writable_file_type = argparse.FileType('w')


def get_read_file_obj(path: str) -> TextIOWrapper:
    """Given a file path, get a readable file object."""
    return open(path, 'r')


def _add_config_path_arg(parser, name, help_msg="Path of configuration file."):
    """"Add configuration file path argument."""
    parser.add_argument(name, type=_readable_file_type, help=help_msg)


def _add_output_path_arg(parser, name, help_msg="Path of output file."):
    """"Add output file path argument."""
    parser.add_argument(name, type=_writable_file_type, help=help_msg)


# TODO: add custom nargs for 2 or more args instead of 1
def _add_results_paths_arg(parser, name, help_msg="Paths of results files."):
    """"Add results files paths argument."""
    parser.add_argument(name,
                        type=_writable_file_type,
                        nargs='+',
                        help=help_msg)


def _add_test_subcommand(subparsers):
    parser_test = subparsers.add_parser('test')
    _add_config_path_arg(parser_test, 'config_path')
    _add_output_path_arg(parser_test, 'output_path')


def _add_plot_subcommand(subparsers):
    parser_plot = subparsers.add_parser('plot')
    _add_config_path_arg(parser_plot, 'config_path')
    _add_results_paths_arg(parser_plot, 'results_paths')


def _add_compare_subcommand(subparsers):
    parser_compare = subparsers.add_parser('compare')
    _add_config_path_arg(parser_compare, 'config_path')
    _add_output_path_arg(parser_compare, 'output_path')
    _add_results_paths_arg(parser_compare, 'results_paths')


_parser = argparse.ArgumentParser(
    description=
    'Run performance tests against the OpenSearch plugin and various ANN libaries.'
)


def define_args():
    """Define tool commands."""
    subparsers = _parser.add_subparsers(title='commands',
                                        dest='command',
                                        help='sub-command help')
    subparsers.required = True

    # add subcommands
    _add_test_subcommand(subparsers)
    _add_plot_subcommand(subparsers)
    _add_compare_subcommand(subparsers)


def get_args() -> Dict[str, Any]:
    """Parses and returns the command line args.

    Returns:
        A dict containing the command line args.
    """
    args = _parser.parse_args()
    return vars(args)
