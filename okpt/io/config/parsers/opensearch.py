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
"""Provides OpenSearchParser.

Classes:
    OpenSearchParser: OpenSearch config parser.
"""
from dataclasses import dataclass
from io import TextIOWrapper
from typing import Any, Dict

from okpt.io.config.parsers import base
from okpt.io.utils import reader


@dataclass
class OpenSearchConfig:
    index_spec: Dict[Any, Any]
    max_num_segments: int
    index_thread: int
    query_thread: int


class OpenSearchParser(base.BaseParser):
    """Parser for OpenSearch config.

    Methods:
        parse: Parse and validate the OpenSearch config.
    """
    def __init__(self):
        super().__init__('opensearch')

    def parse(self, file_obj: TextIOWrapper) -> OpenSearchConfig:
        """See base class."""
        config_obj = super().parse(file_obj)
        index_spec_path = config_obj['index_spec']
        index_spec_obj = reader.parse_json_from_path(index_spec_path)
        opensearch_config = OpenSearchConfig(
            index_spec=index_spec_obj,
            max_num_segments=config_obj['max_num_segments'],
            index_thread=config_obj['index_thread'],
            query_thread=config_obj['query_thread'],
        )
        return opensearch_config
