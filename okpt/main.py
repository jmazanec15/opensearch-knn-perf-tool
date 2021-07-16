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
""" Runner script that serves as the main controller of the testing tool.
"""

import logging
import sys

from okpt.io import args
from okpt.io.config.parsers import base, tool
from okpt.io.utils import writer


def main():
    """Main function of entry module."""
    args.define_args()
    cli_args = args.get_args()

    if cli_args.command == 'test':
        try:
            parser = tool.ToolParser()
            tool_config = parser.parse(cli_args.config_path)
            logging.debug(tool_config)
            logging.debug('configs are valid.')
        except base.ConfigurationError as e:
            logging.error(e.message)
            sys.exit(1)

        # TODO: replace data with test results output
        data = {'a': 1, 'b': 2, 'c': 3}
        output_file_path = cli_args.output_path
        writer.write_json(data, output_file_path)
        logging.debug('data written to `%s`', output_file_path.name)
    elif cli_args.command == 'plot':
        pass  # TODO
    elif cli_args.command == 'compare':
        pass  # TODO
