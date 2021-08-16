from typing import Any, Dict, List

from okpt.io.config.parsers import tool


def _aggregate_steps(steps: List[Dict[str, Any]]):
    results = {'took': {'total': 0}}
    for step in steps:
        label, took = (step['label'], step['took'])
        results['took']['total'] += took
        if label in results['took']:
            results['took'][label] += took
        else:
            results['took'][label] = took

    return results


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
