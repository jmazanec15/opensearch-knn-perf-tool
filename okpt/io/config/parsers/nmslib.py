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
"""Provides NmslibParser.

Classes:
    NmslibParser: NMSLIB config parser.
"""
from dataclasses import dataclass
from io import TextIOWrapper

from okpt.io.config.parsers import base


@dataclass
class MethodParametersConfig:
    ef_construction: int
    ef_search: int
    post: int
    m: int


@dataclass
class MethodConfig:
    name: str
    space_type: str  # not in `parameters` to match OpenSearch config
    parameters: MethodParametersConfig


@dataclass
class NmslibConfig:
    method: MethodConfig
    index_thread_qty: int
    k: int


class NmslibParser(base.BaseParser):
    """Parser for NMSLIB config.

    Methods:
        parse: Parse and validate the NMSLIB config.
    """

    def __init__(self):
        super().__init__('nmslib')

    def parse(self, file_obj: TextIOWrapper) -> NmslibConfig:
        """See base class."""
        config = super().parse(file_obj)
        method_config = config['method']
        parameters_config = method_config['parameters']
        nmslib_config = NmslibConfig(
            method=MethodConfig(
                name=method_config['name'],
                space_type=method_config['space_type'],
                parameters=MethodParametersConfig(
                    ef_construction=parameters_config['ef_construction'],
                    ef_search=parameters_config['ef_search'],
                    m=parameters_config['m'],
                    post=parameters_config['post'],
                )),
            index_thread_qty=config['index_thread_qty'],
            k=config['k'],
        )
        return nmslib_config
