""" Runner script that serves as the main controller of the testing tool.
"""

import sys

import cerberus

from okpt.io import reader, writer
from okpt.io.config import validator


def main():
    reader.define_args()
    args = reader.get_args()

    if args['command'] == 'test':
        data = {'a': 1, 'b': 2, 'c': 3}
        file = args['output_path']
        tool_config_file = args['config_path']
        try:
            are_configs_valid = validator.validate(tool_config_file)
        except Exception as e:
            print(e.args)
            sys.exit(1)

        if (are_configs_valid):
            print('configs are valid!')

        writer.write_json(data, file)
    elif args['command'] == 'plot':
        pass  # TODO
    elif args['command'] == 'compare':
        pass  # TODO
