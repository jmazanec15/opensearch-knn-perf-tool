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

Defines the subcommands `test`, `plot`, and `diff` and the corresponding
files that are required by each command.

Functions:
    define_args(): Define the command line arguments.
    get_args(): Returns a dictionary of the command line args.
"""

import argparse
from dataclasses import dataclass
from io import TextIOWrapper
import os
from typing import List, Union

_readable_file_type = argparse.FileType('r')
_writable_file_type = argparse.FileType('w')


def _add_config_path_arg(parser, name, help_msg='Path of configuration file.'):
    """"Add configuration file path argument."""
    parser.add_argument(name, type=_readable_file_type, help=help_msg)


# TODO: add custom nargs for 2 or more args instead of 1
def _add_result_paths_arg(parser, name, help_msg='Paths of results files.'):
    """"Add results files paths argument."""
    parser.add_argument(
        name,
        type=_readable_file_type,
        nargs='+',
        help=help_msg,
    )


def _add_output_path_arg(parser, name, help_msg='Path of output file.'):
    """"Add output file path argument."""
    parser.add_argument(
        name,
        type=_writable_file_type,
        help=help_msg,
        default=os.devnull,
    )


def _add_test_subcommand(subparsers):
    test_parser = subparsers.add_parser('test')
    _add_config_path_arg(test_parser, 'config_path')
    _add_output_path_arg(test_parser, 'output_path')


def _add_diff_subcommand(subparsers):
    diff_parser = subparsers.add_parser('diff')
    _add_result_paths_arg(diff_parser, 'result_paths')
    _add_output_path_arg(diff_parser, '--output_path')


def _add_plot_subcommand(subparsers):
    plot_parser = subparsers.add_parser('plot')
    _add_result_paths_arg(plot_parser, 'result_paths')
    _add_output_path_arg(plot_parser, 'output_path')


_parser = argparse.ArgumentParser(
    description=
    'Run performance tests against the OpenSearch plugin and various ANN libaries.'
)


def define_args():
    """Define tool commands."""
    _parser.add_argument('--log',
                         type=str,
                         choices=[
                             'debug',
                             'info',
                             'warning',
                             'error',
                             'critical',
                         ],
                         default='info')
    subparsers = _parser.add_subparsers(
        title='commands',
        dest='command',
        help='sub-command help',
    )
    subparsers.required = True

    # add subcommands
    _add_test_subcommand(subparsers)
    _add_diff_subcommand(subparsers)
    _add_plot_subcommand(subparsers)


@dataclass
class TestArgs:
    log: str
    command: str
    config: TextIOWrapper
    output: TextIOWrapper


@dataclass
class DiffArgs:
    log: str
    command: str
    results: List[TextIOWrapper]
    output: TextIOWrapper


def get_args() -> Union[TestArgs, DiffArgs]:
    """Parses and returns the command line args.

    Returns:
        A dict containing the command line args.
    """
    args = _parser.parse_args()
    if args.command == 'test':
        return TestArgs(log=args.log,
                        command=args.command,
                        config=args.config_path,
                        output=args.output_path)
    else:
        return DiffArgs(log=args.log,
                        command=args.command,
                        results=args.result_paths,
                        output=args.output_path)
