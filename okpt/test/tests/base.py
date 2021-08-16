from typing import Any, Dict, List

from okpt.io.config.parsers import tool


def _aggregate_steps(steps: List[Dict[str, Any]], measures=['took']):
    results = {'took_total': 0}
    for step in steps:
        label = step['label']
        for measure in measures:
            if measure in step:
                measure_label = f'{measure}_{label}'
                measure_total_label = f'{measure}_total'
                if not measure_total_label in results:
                    results[measure_total_label] = 0

                step_measure = step[measure]
                results[measure_total_label] += step_measure
                if measure_label in results:
                    results[measure_label] += step_measure
                else:
                    results[measure_label] = step_measure

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
