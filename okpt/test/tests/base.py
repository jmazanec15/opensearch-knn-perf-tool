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
"""Provides a base Test class."""
from math import floor
from typing import Any, Dict, List

from okpt.io.config.parsers import tool


def _pxx(values: List[Any], p: float):
    """Calculates the pXX statistics for a given list.

    Args:
        values: List of values.
        p: Percentile (between 0 and 1).

    Returns:
        The corresponding pXX metric.
    """
    lowest_percentile = 1 / len(values)
    highest_percentile = (len(values) - 1) / len(values)

    # return -1 if p is out of range or if the list doesn't have enough elements
    # to support the specified percentile
    if p < 0 or p > 1:
        return -1
    elif p < lowest_percentile or p > highest_percentile:
        return -1
    else:
        return values[floor(len(values) * p)]


def _aggregate_steps(steps: List[Dict[str, Any]], measure_labels=['took']):
    """Aggregates the steps for a given Test.

    The aggregation process extracts the measures from each step and calculates
    the total time spent performing each step measure, including the
    percentile metrics, if possible.

    The aggregation process also extracts the test measures by simply summing
    up the respective step measures.

    A step measure is formatted as `{step_name}_{measure_name}`, for example,
    {bulk_index}_{took} or {query_index}_{memory}. The braces are not included
    in the actual key string.

    Percentile/Total step measures are give as
    `{step_name}_{measure_name}_{percentile|total}`.

    Test measures are just step measure sums so they just given as
    `test_{measure_name}`.

    Args:
        steps: List of test steps to be aggregated.
        measures: List of step metrics to account for.

    Returns:
        A complete test result.
    """
    test_measures = {
        f'test_{measure_label}': 0
        for measure_label in measure_labels
    }
    step_measures: Dict[str, Any] = {}

    # iterate over all test steps
    for step in steps:
        step_label = step['label']

        # iterate over all measures in each test step
        for measure_label in measure_labels:
            # not all step results contain the same measures, so only include
            # possible measures
            if measure_label in step:
                step_measure = step[measure_label]
                step_measure_label = f'{step_label}_{measure_label}'

                test_measures[f'test_{measure_label}'] += step_measure
                if step_measure_label in step_measures:
                    step_measures[step_measure_label].append(step_measure)
                else:
                    step_measures[step_measure_label] = [step_measure]

    aggregate = {**test_measures}
    # calculate the totals and percentile statistics for each step measure
    for step_measure_label, step_measure in step_measures.items():
        step_measure.sort()
        aggregate[step_measure_label + '_total'] = sum(step_measure)
        aggregate[step_measure_label + '_p50'] = _pxx(step_measure, 0.50)
        aggregate[step_measure_label + '_p90'] = _pxx(step_measure, 0.90)
        aggregate[step_measure_label + '_p99'] = _pxx(step_measure, 0.99)

    return aggregate


class Test():
    """A base Test class, representing a collection of steps to profiled and aggregated.

    Methods:
        setup: Performs test setup. Usually for steps not intended to be profiled.
        run_steps: Runs the test steps, aggregating the results into the `step_results` instance field.
        cleanup: Perform test cleanup. Useful for clearing the state of a persistent process like OpenSearch.
        execute: Runs steps, cleans up, and aggregates the test result.
    """
    def __init__(self, service_config, dataset: tool.Dataset):
        """Initializes the test state.

        Args:
            service_config: Config of respective k-NN service.
            dataset: Dataset of vectors to use for testing.
        """
        self.service_config = service_config
        self.dataset = dataset
        self.step_results: List[Dict[str, Any]] = []

    def setup(self):
        pass

    def _run_steps(self):
        pass

    def _cleanup(self):
        pass

    def execute(self):
        self._run_steps()
        self._cleanup()
        return _aggregate_steps(self.step_results)
