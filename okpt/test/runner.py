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
"""Provides a test runner class."""
import dataclasses
import platform
import sys
from datetime import datetime
from typing import Any, Dict, List

import psutil

from okpt.io.config.parsers import base, tool
from okpt.test.tests import nmslib, opensearch


def _get_test(test_id: int):
    """Returns the Test class matching the test_id.

    Args:
        test_id: ID of Test.

    Returns:
        The Test class matching the test_id.
    """
    if test_id == 1:
        return opensearch.OpenSearchIndexTest
    elif test_id == 2:
        return opensearch.OpenSearchQueryTest
    elif test_id == 3:
        return nmslib.NmslibIndexTest
    elif test_id == 4:
        return nmslib.NmslibQueryTest
    else:
        raise base.ConfigurationError(message='Invalid test_id.')


def _get_avg(values: List[Any]):
    """Get average value of a list.

    Args:
        values: A list of values.

    Returns:
        The average value in the list.
    """
    return sum(values) / len(values)


def _aggregate_runs(runs: List[Dict[Any, Any]]):
    """Aggregates and averages a list of test results.

    Args:
        results: A list of test results.
        num_runs: Number of times the tests were ran.

    Returns:
        A dictionary containing the averages of the test results.
    """
    aggregate: Dict[str, Any] = {}
    for run in runs:
        for key, value in run.items():
            if key in aggregate:
                aggregate[key].append(value)
            else:
                aggregate[key] = [value]

    aggregate = {key: _get_avg(value) for key, value in aggregate.items()}
    return aggregate


class TestRunner():
    """Test runner class for running tests and aggregating the results.

    Methods:
        execute: Run the tests and aggregate the results.
    """
    def __init__(self, tool_config: tool.ToolConfig):
        """"Initializes test state and chooses the appropriate Test."""
        self.tool_config = tool_config
        self.test_class = _get_test(tool_config.test_id)

    def _get_metadata(self):
        """"Retrieves the test metadata."""
        svmem = psutil.virtual_memory()
        return {
            'test_name':
            self.tool_config.test_name,
            'test_id':
            self.tool_config.test_id,
            'date':
            datetime.now().strftime('%m/%d/%Y %H:%M:%S'),
            'python_version':
            sys.version,
            'os_version':
            platform.platform(),
            'processor':
            platform.processor() + ', ' + str(psutil.cpu_count(logical=True)) +
            ' cores',
            'memory':
            str(svmem.used) + ' (used) / ' + str(svmem.available) +
            ' (available) / ' + str(svmem.total) + ' (total)',
        }

    def execute(self):
        """Runs the tests and aggregates the results.

        Returns:
            A dictionary containing the aggregate of test results.
        """
        runs = []
        for _ in range(self.tool_config.test_parameters.num_runs):
            self.test = self.test_class(
                service_config=self.tool_config.service_config,
                dataset=self.tool_config.dataset)
            self.test.setup()
            run = self.test.execute()
            runs.append(run)

        aggregate = _aggregate_runs(runs)

        # add metadata to test results
        tool_result = {
            **self._get_metadata(), 'aggregate': aggregate,
            'test_parameters':
            dataclasses.asdict(self.tool_config.test_parameters)
        }

        # include info about all test runs if specified in config
        if self.tool_config.test_parameters.show_runs:
            tool_result['runs'] = runs

        return tool_result
