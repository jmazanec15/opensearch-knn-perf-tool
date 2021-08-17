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
""" Runner script that serves as the main controller of the testing tool."""

import json
import logging
import sys

from okpt.io import args
from okpt.io.config.parsers import base, tool
from okpt.io.utils.writer import write_json
from okpt.test import runner


def main():
    """Main function of entry module."""
    args.define_args()
    cli_args = args.get_args()
    output = cli_args.output
    if cli_args.log:
        log_level = getattr(logging, cli_args.log.upper())
        logging.basicConfig(level=log_level)

    if cli_args.command == 'test':
        try:
            parser = tool.ToolParser()
            tool_config = parser.parse(cli_args.config)
            logging.info('Configs are valid.')

            test_runner = runner.TestRunner(tool_config=tool_config)
            test_result = test_runner.execute()
            logging.info(json.dumps(test_result, indent=2))
            write_json(data=test_result, file=output)
        except base.ConfigurationError as e:
            logging.error(e.message)
            sys.exit(1)

    elif cli_args.command == 'plot':
        pass  # TODO
    elif cli_args.command == 'compare':
        pass  # TODO
