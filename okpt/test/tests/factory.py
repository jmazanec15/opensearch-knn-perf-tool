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
"""Provides a factory class for tests."""
from okpt.io.config.parsers import base as base_p
from okpt.io.config.parsers import tool
from okpt.test.tests import base as base_t
from okpt.test.tests import nmslib, opensearch

_tests = {
    'opensearch_index': opensearch.OpenSearchIndexTest,
    'opensearch_query': opensearch.OpenSearchQueryTest,
    'nmslib_index': nmslib.NmslibIndexTest,
    'nmslib_query': nmslib.NmslibQueryTest,
}


def TestFactory(tool_config: tool.ToolConfig) -> base_t.Test:
    """Factory function for tests.

    Args:
        tool_config: Performance tool configuration.

    Returns:
        Test matching test_id.

    Raises:
        ConfigurationError: If the provided test_id doesn't match a defined test.
    """
    if not tool_config.test_id in _tests:
        raise base_p.ConfigurationError(message='Invalid test_id.')

    return _tests[tool_config.test_id](tool_config.service_config,
                                       tool_config.dataset)
