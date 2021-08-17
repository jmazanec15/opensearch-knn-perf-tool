from math import floor
from typing import Any, Dict, List

from okpt.io.config.parsers import tool


def _pX(values: List[Any], p: float):
    lowest_percentile = 1 / len(values)
    highest_percentile = (len(values) - 1) / len(values)
    if p < 0 or p > 1:
        return -1
    elif p < lowest_percentile or p > highest_percentile:
        return -1
    else:
        return values[floor(len(values) * p)]


def _aggregate_steps(steps: List[Dict[str, Any]], measures=['took']):
    step_measure_labels = {}
    for step in steps:
        step_label = step['label']
        for measure in measures:
            if measure in step:
                step_measure = step[measure]
                step_measure_label = f'{step_label}_{measure}'

                if step_measure_label in step_measure_labels:
                    step_measure_labels[step_measure_label].append(
                        step_measure)
                else:
                    step_measure_labels[step_measure_label] = [step_measure]

    aggregate = {}
    for step_measure_label, step_measures in step_measure_labels.items():
        step_measures.sort()
        aggregate[step_measure_label + '_total'] = sum(step_measures)
        aggregate[step_measure_label + '_p50'] = _pX(step_measures, 0.50)
        aggregate[step_measure_label + '_p90'] = _pX(step_measures, 0.90)
        aggregate[step_measure_label + '_p99'] = _pX(step_measures, 0.99)

    return aggregate


class Test():
    def __init__(self, service_config, dataset: tool.Dataset):
        self.service_config = service_config
        self.dataset = dataset
        self.bulk_size = 5000
        self.step_results = []

    def setup(self):
        pass

    def run_steps(self):
        pass

    def cleanup(self):
        pass

    def execute(self):
        self.run_steps()
        self.cleanup()
        return _aggregate_steps(self.step_results)
