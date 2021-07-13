""" Runner script that serves as the main controller of the testing tool.
"""

import sys

from okpt.io import reader, writer
from okpt.io.config import validator


def main():
    """Main function of entry module."""
    reader.define_args()
    args = reader.get_args()

    if args['command'] == 'test':
        tool_config_file_obj = args['config_path']
        try:
            tool_config, service_config, index_settings = validator.validate(
                tool_config_file_obj)
            print('configs are valid!')
        except validator.ConfigurationError as e:
            print(e.args)
            sys.exit(1)

        data = {'a': 1, 'b': 2, 'c': 3}
        output_file_path = args['output_path']
        writer.write_json(data, output_file_path)
        print(f'data written to `{output_file_path.name}`')
    elif args['command'] == 'plot':
        pass  # TODO
    elif args['command'] == 'compare':
        pass  # TODO
