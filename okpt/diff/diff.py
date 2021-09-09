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


class InvalidTestResultsError(Exception):
    """Exception raised when the test results are invalid.

    The results can be invalid if they have different fields, non-numeric
    values, or if they don't follow the standard result format.
    """
    def __init__(self, msg: str):
        self.message = msg
        super().__init__(self.message)


def _is_numeric(a) -> bool:
    return isinstance(a, (int, float))


class Diff:
    """Diff class for validating and diffing two test result files.

    Methods:
        diff: Returns the diff between two test results. (changed - base)
    """
    def __init__(
        self,
        base_result: Dict[str,
                          Any],
        changed_result: Dict[str,
                             Any],
        metadata: bool
    ):
        """Initializes test results and validate them."""
        self.base_result = base_result
        self.changed_result = changed_result
        self.metadata = metadata

        # make sure results have proper test result fields
        is_valid, key, result = self._validate_keys()
        if not is_valid:
            raise InvalidTestResultsError(
                f'{result} has a missing or invalid key `{key}`.'
            )

        self.base_results = self.base_result['results']
        self.changed_results = self.changed_result['results']

        # make sure results have the same fields
        is_valid, key, result = self._validate_structure()
        if not is_valid:
            raise InvalidTestResultsError(
                f'key `{key}` is not present in {result}.'
            )

        # make sure results have numeric values
        is_valid, key, result = self._validate_types()
        if not is_valid:
            raise InvalidTestResultsError(
                f'key `{key}` in {result} points to a non-numeric value.'
            )

    def _validate_keys(self) -> Tuple[bool, str, str]:
        """Ensure both test results have `metadata` and `results` keys."""
        check_keydict = lambda key, res: key in res and isinstance(
            res[key], dict)

        # check if results have a `metadata` field and if `metadata` is a dict
        if self.metadata:
            if not check_keydict('metadata', self.base_result):
                return (False, 'metadata', 'base_result')
            if not check_keydict('metadata', self.changed_result):
                return (False, 'metadata', 'changed_result')
        # check if results have a `results` field and `results` is a dict
        if not check_keydict('results', self.base_result):
            return (False, 'results', 'base_result')
        if not check_keydict('results', self.changed_result):
            return (False, 'results', 'changed_result')
        return (True, '', '')

    def _validate_structure(self) -> Tuple[bool, str, str]:
        """Ensure both test results have the same keys."""
        for k in self.base_results:
            if not k in self.changed_results:
                return (False, k, 'changed_result')
        for k in self.changed_results:
            if not k in self.base_results:
                return (False, k, 'base_result')
        return (True, '', '')

    def _validate_types(self) -> Tuple[bool, str, str]:
        """Ensure both test results have numeric values."""
        for k, v in self.base_results.items():
            if not _is_numeric(v):
                return (False, k, 'base_result')
        for k, v in self.changed_results.items():
            if not _is_numeric(v):
                return (False, k, 'changed_result')
        return (True, '', '')

    def diff(self) -> Dict[str, Any]:
        """Return the diff between the two test results. (changed - base)"""
        results_diff = {
            key: self.changed_results[key] - self.base_results[key]
            for key in self.base_results
        }

        # add metadata if specified
        if self.metadata:
            return {
                'base_metadata': self.base_result['metadata'],
                'changed_metadata': self.changed_result['metadata'],
                'diff': results_diff
            }
        return results_diff
