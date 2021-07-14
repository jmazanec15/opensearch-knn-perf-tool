# SPDX-License-Identifier: Apache-2.0

# The OpenSearch Contributors require contributions made to
# this file be licensed under the Apache-2.0 license or a
# compatible open source license.

# Modifications Copyright OpenSearch Contributors. See
# GitHub history for details.
""" Runner script that serves as the main controller of the testing tool.
"""

import sys
import logging

from okpt.io import reader, writer
from okpt.io.config import validator


def main():
    """Main function of entry module."""
    reader.define_args()
    args = reader.get_args()

    if args['command'] == 'test':
        tool_config_file_obj = args['config_path']
        try:
            tool_config, service_config, index_spec = validator.validate(
                tool_config_file_obj)
            logging.debug('configs are valid!')
        except validator.ConfigurationError as e:
            logging.error(e.args)
            sys.exit(1)

        # TODO: replace data with test results output
        data = {'a': 1, 'b': 2, 'c': 3}
        output_file_path = args['output_path']
        writer.write_json(data, output_file_path)
        logging.debug(f'data written to `{output_file_path.name}`')
    elif args['command'] == 'plot':
        pass  # TODO
    elif args['command'] == 'compare':
        pass  # TODO
