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
"""Provides ToolParser.

Classes:
    ToolParser: Tool config parser.
"""
from io import TextIOWrapper
from typing import Any, Dict

from okpt.io.config.parsers import base, utils
from okpt.io.utils import reader


class ToolParser(base.BaseParser):
    """Parser for Tool config.

    Methods:
        parse: Parse and validate the Tool config.
    """
    def __init__(self):
        super().__init__('tool')

    def parse(self, file_obj: TextIOWrapper) -> Dict[str, Any]:
        """See base class."""
        config_obj = super().parse(file_obj)

        # determine which knn_service is used
        knn_service_name = config_obj['knn_service']
        service_config_path = config_obj['service_config']
        service_config_file_obj = reader.get_file_obj(service_config_path)
        config_parser = utils.get_parser(knn_service_name)
        return {
            **config_obj, 'service_config':
            config_parser.parse(service_config_file_obj)
        }
