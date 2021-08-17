# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Parses and defines command line arguments for the program.

Defines the subcommands `test`, `plot`, and `compare` and the corresponding
files that are required by each command.

Functions:
    define_args(): Define the command line arguments.
    get_args(): Returns a dictionary of the command line args.
"""

import argparse
from dataclasses import dataclass
from io import TextIOWrapper

_readable_file_type = argparse.FileType('r')
_writable_file_type = argparse.FileType('w')


def _add_config_path_arg(parser, name, help_msg='Path of configuration file.'):
    """"Add configuration file path argument."""
    parser.add_argument(name, type=_readable_file_type, help=help_msg)


def _add_output_path_arg(parser, name, help_msg='Path of output file.'):
    """"Add output file path argument."""
    parser.add_argument(name, type=_writable_file_type, help=help_msg)


# TODO: add custom nargs for 2 or more args instead of 1
def _add_results_paths_arg(parser, name, help_msg='Paths of results files.'):
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
    _parser.add_argument(
        '--log',
        type=str,
        choices=['debug', 'info', 'warning', 'error', 'critical'])
    subparsers = _parser.add_subparsers(title='commands',
                                        dest='command',
                                        help='sub-command help')
    subparsers.required = True

    # add subcommands
    _add_test_subcommand(subparsers)
    _add_plot_subcommand(subparsers)
    _add_compare_subcommand(subparsers)


@dataclass
class ToolArgs:
    log: str
    command: str
    config: TextIOWrapper
    output: TextIOWrapper


def get_args() -> ToolArgs:
    """Parses and returns the command line args.

    Returns:
        A dict containing the command line args.
    """
    args = _parser.parse_args()
    tool_args = ToolArgs(log=args.log,
                         command=args.command,
                         config=args.config_path,
                         output=args.output_path)
    return tool_args
