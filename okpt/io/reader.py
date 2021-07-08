"""Parses and defines command line arguments for the program.

Defines the subcommands `test`, `plot`, and `compare` and the corresponding
files that are required by each command.

Functions:
    get_args(): returns a dictionary of the command line args
"""

import argparse

parser = argparse.ArgumentParser(
    description=
    'Run performance tests against the OpenSearch plugin and various ANN libaries.'
)

readable_file_type = argparse.FileType('r')
writable_file_type = argparse.FileType('w')


def add_config_path_arg(parser, name, help_msg="Path of configuration file."):
    parser.add_argument(name, type=readable_file_type, help=help_msg)


def add_output_path_arg(parser, name, help_msg="Path of output file."):
    parser.add_argument(name, type=writable_file_type)


# TODO: add custom nargs for 2 or more args instead of 1
def add_results_paths_arg(parser, name, help_msg="Paths of results files."):
    parser.add_argument(name,
                        type=writable_file_type,
                        nargs='+',
                        help=help_msg)


def define_args():
    subparsers = parser.add_subparsers(title='commands',
                                       dest='command',
                                       help='sub-command help')

    # add subcommands
    parser_test = subparsers.add_parser('test')
    parser_plot = subparsers.add_parser('plot')
    parser_compare = subparsers.add_parser('compare')

    # test subcommand
    add_config_path_arg(parser_test, 'config_path')
    add_output_path_arg(parser_test, 'output_path')

    # plot subcommand
    add_config_path_arg(parser_plot, 'config_path')
    add_results_paths_arg(parser_plot, 'results_paths')

    # compare subcommand
    add_config_path_arg(parser_compare, 'config_path')
    add_output_path_arg(parser_compare, 'output_path')
    add_results_paths_arg(parser_compare, 'results_paths')


def get_args():
    args = parser.parse_args()
    return vars(args)
