"""Parses and defines command line arguments for the program.

Defines the subcommands `test`, `plot`, and `compare` and the corresponding
files that are required by each command.

get_args(): returns a dictionary of the command line args
"""

import argparse

parser = argparse.ArgumentParser(
    description=
    'Run performance tests against the OpenSearch plugin and various ANN libaries.'
)


def define_args():
    subparsers = parser.add_subparsers(help='sub-command help')

    # add subcommands
    parser_test = subparsers.add_parser('test')
    parser_plot = subparsers.add_parser('plot')
    parser_compare = subparsers.add_parser('compare')

    readable_file_type = argparse.FileType('r')
    writable_file_type = argparse.FileType('w')

    # test subcommand
    parser_test.add_argument('config_path',
                             type=readable_file_type,
                             help='Path of configuration file.')
    parser_test.add_argument('output_path',
                             type=writable_file_type,
                             help='Path of output file.')

    # plot subcommand
    parser_plot.add_argument('config_path',
                             type=readable_file_type,
                             help='Path of configuration file.')
    parser_plot.add_argument('results_paths',
                             type=readable_file_type,
                             nargs='+',
                             help='Paths of result files.')

    # compare subcommand
    parser_compare.add_argument('config_path',
                                type=readable_file_type,
                                help='Path of configuration file.')
    parser_compare.add_argument('output_path',
                                type=writable_file_type,
                                help='Path of output file.')
    parser_compare.add_argument('results_paths',
                                type=readable_file_type,
                                nargs='+',
                                help='Paths of result files.')


def get_args():
    args = parser.parse_args()
    return vars(args)
