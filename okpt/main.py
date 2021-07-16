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

from okpt.io.config import parser
from okpt.io.utils import reader, writer


def main():
    """Main function of entry module."""
    reader.define_args()
    args = reader.get_args()

    if args.command == 'test':
        tool_config_file_obj = args.config_path
        try:
            tool_config, service_config, index_spec = parser.validate(
                tool_config_file_obj)
            logging.debug('configs are valid!')
        except parser.ConfigurationError as e:
            logging.error(e.args)
            sys.exit(1)

        # TODO: replace data with test results output
        data = {'a': 1, 'b': 2, 'c': 3}
        output_file_path = args.output_path
        writer.write_json(data, output_file_path)
        logging.debug('data written to `%s`', output_file_path.name)
    elif args.command == 'plot':
        pass  # TODO
    elif args.command == 'compare':
        pass  # TODO
