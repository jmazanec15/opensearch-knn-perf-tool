from typing import Any, Dict, List

import h5py
from elasticsearch import Elasticsearch, RequestsHttpConnection
from okpt.io.config.parsers import tool
from okpt.io.config.parsers.nmslib import NmslibConfig
from okpt.io.config.parsers.opensearch import OpenSearchConfig
from okpt.test import nmslib, opensearch


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


class OpenSearchTest(Test):
    def __init__(self, service_config: OpenSearchConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.index_name = 'test_index'
        self.es = Elasticsearch(hosts=[{
            'host': 'localhost',
            'port': 9200
        }],
                                use_ssl=False,
                                verify_certs=False,
                                connection_class=RequestsHttpConnection)

    def setup(self):
        body = {
            'transient': {
                'knn.algo_param.index_thread_qty':
                self.service_config.index_thread
            }
        }
        self.es.cluster.put_settings(body=body)


class OpenSearchIndexTest(OpenSearchTest):
    def __init__(self, service_config: OpenSearchConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.action = {'index': {'_index': self.index_name}}

    def setup(self):
        super().setup()

        # split training set into sections for bulk ingestion
        bulk_size = 5000
        self.sections = opensearch.bulk_transform_vectors(
            self.dataset.train, self.action, bulk_size)

    def run_steps(self):
        self.step_results += [
            opensearch.create_index(self.es, self.index_name,
                                    self.service_config.index_spec),
            *opensearch.bulk_index(self.es, self.index_name, self.sections),
            opensearch.refresh_index(self.es, self.index_name)
        ]

    def cleanup(self):
        opensearch.delete_index(es=self.es, index_name=self.index_name)


class OpenSearchQueryTest(OpenSearchTest):
    def __init__(self, service_config: OpenSearchConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.action = {'index': {'_index': self.index_name}}

    def setup(self):
        super().setup()

        # split training set into sections for bulk ingestion
        bulk_size = 5000
        self.sections = opensearch.bulk_transform_vectors(
            self.dataset.train, self.action, bulk_size)
        opensearch.create_index(self.es, self.index_name,
                                self.service_config.index_spec)
        opensearch.bulk_index(self.es, self.index_name, self.sections)

    def run_steps(self):
        for vec in self.dataset.test:
            k = 10
            body = {
                'size': 10,
                'query': {
                    'knn': {
                        'test_vector': {
                            'vector': vec,
                            'k': k
                        }
                    }
                }
            }
            result = opensearch.query_index(es=self.es,
                                            index_name=self.index_name,
                                            body=body)
            self.step_results.append(result)

    def cleanup(self):
        opensearch.delete_index(es=self.es, index_name=self.index_name)


class NmslibIndexTest(Test):
    def __init__(self, service_config: NmslibConfig, dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.dataset = dataset

    def run_steps(self):
        result = nmslib.init_index(space=self.service_config.method.space)
        self.index = result['index']
        self.step_results += [
            result,
            nmslib.bulk_index(index=self.index, dataset=self.dataset.train[:]),
            nmslib.create_index(index=self.index)
        ]


class NmslibQueryTest(Test):
    def __init__(self, service_config: NmslibConfig, dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.dataset = dataset

    def setup(self):
        result = nmslib.init_index(space=self.service_config.method.space)
        self.index = result['index']
        nmslib.bulk_index(index=self.index, dataset=self.dataset.train[:])
        nmslib.create_index(index=self.index)

    def run_steps(self):
        for vec in self.dataset.train:
            k = 10
            result = nmslib.query_index(index=self.index, vector=vec, k=k)
            self.step_results.append(result)
