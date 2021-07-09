"""Parses and defines command line arguments for the program.

Defines the subcommands `test`, `plot`, and `compare` and the corresponding
files that are required by each command.

Functions:
    get_args(): returns a dictionary of the command line args
"""

import argparse

readable_file_type = argparse.FileType('r')
writable_file_type = argparse.FileType('w')


def add_config_path_arg(parser, name, help_msg="Path of configuration file."):
    """"Add configuration file path argument."""
    parser.add_argument(name, type=readable_file_type, help=help_msg)


def add_output_path_arg(parser, name, help_msg="Path of output file."):
    """"Add output file path argument."""
    parser.add_argument(name, type=writable_file_type, help=help_msg)


# TODO: add custom nargs for 2 or more args instead of 1
def add_results_paths_arg(parser, name, help_msg="Paths of results files."):
    """"Add results files paths argument."""
    parser.add_argument(name,
                        type=writable_file_type,
                        nargs='+',
                        help=help_msg)


def add_test_subcommand(subparsers):
    parser_test = subparsers.add_parser('test')
    add_config_path_arg(parser_test, 'config_path')
    add_output_path_arg(parser_test, 'output_path')


def add_plot_subcommand(subparsers):
    parser_plot = subparsers.add_parser('plot')
    add_config_path_arg(parser_plot, 'config_path')
    add_results_paths_arg(parser_plot, 'results_paths')


def add_compare_subcommand(subparsers):
    parser_compare = subparsers.add_parser('compare')
    add_config_path_arg(parser_compare, 'config_path')
    add_output_path_arg(parser_compare, 'output_path')
    add_results_paths_arg(parser_compare, 'results_paths')


parser = argparse.ArgumentParser(
    description=
    'Run performance tests against the OpenSearch plugin and various ANN libaries.'
)
def define_args():
    subparsers = parser.add_subparsers(title='commands',
                                       dest='command',
                                       help='sub-command help')

    # add subcommands
    add_test_subcommand(subparsers)
    add_plot_subcommand(subparsers)
    add_compare_subcommand(subparsers)


def get_args():
    args = parser.parse_args()
    return vars(args)
