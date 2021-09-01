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
"""Provides the Diff class."""

from typing import Any, Dict, Tuple


class InconsistentTestResultsError(Exception):
    """Exception raised when two test results have different keys.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, key: str, result: str):
        self.message = f'key `{key}` is not present in {result}.'
        super().__init__(self.message)


class InvalidTestResultsType(Exception):
    """Exception raised when a test result has non-numeric test result values.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, key: str, result: str):
        self.message = f'key `{key}` in {result} points to a non-numeric value.'
        super().__init__(self.message)


def _is_numeric(a) -> bool:
    return type(a) == int or type(a) == float


class Diff:
    """Diff class for validating and diffing two test result files.

    Methods:
        diff: Returns the diff between two test results. (right minus left)
    """

    def __init__(self, l_result: Dict[str, Any], r_result: Dict[str, Any]):
        """Initializes test results and validate them."""
        self.l_result = l_result['results']
        self.r_result = r_result['results']

        # validate test results
        is_valid, key, result = self._validate_structure()
        if not is_valid:
            raise InconsistentTestResultsError(key, result)
        is_valid, key, result = self._validate_types()
        if not is_valid:
            raise InvalidTestResultsType(key, result)

    def _validate_structure(self) -> Tuple[bool, str, str]:
        """Ensure both test results have the same keys."""
        for k in self.l_result:
            if not k in self.r_result:
                return (False, k, 'right_result')
        for k in self.r_result:
            if not k in self.l_result:
                return (False, k, 'left_result')
        return (True, '', '')

    def _validate_types(self) -> Tuple[bool, str, str]:
        """Ensure both test results have numeric values."""
        for k, v in self.l_result.items():
            if not _is_numeric(v):
                return (False, k, 'left_result')
        for k, v in self.r_result.items():
            if not _is_numeric(v):
                return (False, k, 'right_result')
        return (True, '', '')

    def diff(self) -> Dict[str, Any]:
        """Return the diff between the two test results. (right minus left)"""
        return {
            key: self.r_result[key] - self.l_result[key]
            for key in self.l_result
            if isinstance(self.l_result[key], int) or
            isinstance(self.l_result[key], float)
        }
