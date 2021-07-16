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
from io import TextIOWrapper
from typing import Any, Dict

from okpt.io.config.parsers import base


class NmslibParser(base.BaseParser):
    """Parser for NMSLIB config.

    Methods:
        parse: Parse and validate the NMSLIB config.
    """
    def __init__(self):
        super().__init__('nmslib')

    def parse(self, file_obj: TextIOWrapper) -> Dict[str, Any]:
        """See base class."""
        config_obj = super().parse(file_obj)
        return config_obj
