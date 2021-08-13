from typing import Any, Dict

from okpt.io.config.parsers.tool import ToolConfig
from okpt.test.services.base import Service
from okpt.test.services.nmslib import NmslibService
from okpt.test.services.opensearch import OpenSearchService


def _get_service(tool_config: ToolConfig) -> Service:
    _INDEX_NAME = 'test_index'
    service_name = tool_config.knn_service
    service_config = tool_config.service_config
    if service_name == 'opensearch':
        return OpenSearchService(_INDEX_NAME, service_config.index_spec)
    elif service_name == 'nmslib':
        return NmslibService(service_config['method']['space_type'])
    else:
        raise Exception()


class Tester():
    def __init__(self, tool_config: ToolConfig, test_type: str, num_runs: int,
                 dataset):
        self.service = _get_service(tool_config)
        self.test_type = test_type
        self.training_set = dataset['train']
        self.testing_set = dataset['test']
        self.num_runs = num_runs
        self.results = []

    def test(self):
        test_result = None
        if self.test_type == 'index':
            for _ in range(self.num_runs):
                test_result = self.service.bulk_index(self.training_set)
                self.results.append(test_result)
        elif self.test_type == 'query':
            test_result = self.service.bulk_index(self.training_set)
            for _ in range(self.num_runs):
                for vec in self.testing_set[:5]:
                    test_result = self.service.query(vec)
                self.results.append(test_result)
        self.results.append(test_result)

    def get_results(self):
        return self.results

    def reset(self):
        self.results = []
