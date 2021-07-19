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
"""Provides utility functions for the module.

Functions:
    get_parser(): Return the intended parser.
"""
from okpt.io.config.parsers import base, nmslib, opensearch, tool


def get_parser(parser_name: str) -> base.BaseParser:
    """Given a parser name, return the corresponding parser.

    Args:
        parser_name: Name of parser.

    Returns:
        Parser for the corresponding config.
    """
    if parser_name == 'tool':
        return tool.ToolParser()
    if parser_name == 'opensearch':
        return opensearch.OpenSearchParser()
    if parser_name == 'nmslib':
        return nmslib.NmslibParser()

    raise Exception(f'Invalid parser `{parser_name}`.')
