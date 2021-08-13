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
    def setup(self):
        pass

    def execute(self):
        pass


class OpenSearchTest(Test):
    def __init__(self, service_config: OpenSearchConfig):
        self.index_name = 'test_index'
        self.service_config = service_config
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

    def execute(self):
        pass


class OpenSearchIndexTest(OpenSearchTest):
    def __init__(self, service_config: OpenSearchConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config)
        self.dataset = dataset
        self.action = {'index': {'_index': self.index_name}}

    def setup(self):
        super().setup()

        # split training set into sections for bulk ingestion
        bulk_size = 1000
        self.sections = opensearch.bulk_transform_vectors(
            self.dataset.train, self.action, bulk_size)

    def index_vectors(self):
        results = []

        results.append(
            opensearch.create_index(self.es, self.index_name,
                                    self.service_config.index_spec))
        results += opensearch.bulk_index(self.es, self.index_name,
                                         self.sections)
        results.append(opensearch.refresh_index(self.es, self.index_name))

        return results

    def cleanup(self):
        opensearch.delete_index(es=self.es, index_name=self.index_name)

    def execute(self):
        step_results = self.index_vectors()
        test_result = _aggregate_steps(step_results)
        self.cleanup()
        return test_result


class OpenSearchQueryTest(OpenSearchTest):
    def __init__(self, service_config: OpenSearchConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config)
        self.dataset = dataset
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

    def query_vectors(self, dataset: h5py.Dataset):
        results = []

        for vec in dataset:
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
            results.append(result)

        return results

    def cleanup(self):
        opensearch.delete_index(es=self.es, index_name=self.index_name)

    def execute(self):
        step_results = self.query_vectors(self.dataset.test)
        test_result = _aggregate_steps(step_results)
        self.cleanup()
        return test_result


class NmslibIndexTest(Test):
    def __init__(self, service_config: NmslibConfig, dataset: tool.Dataset):
        self.service_config = service_config
        self.dataset = dataset

    def index_vectors(self):
        results = []
        result = nmslib.init_index(space=self.service_config.method.space)
        self.index = result['index']
        results.append(result)
        results.append(
            nmslib.bulk_index(index=self.index, dataset=self.dataset.train[:]))
        results.append(nmslib.create_index(index=self.index))
        return results

    def execute(self):
        step_results = self.index_vectors()
        test_result = _aggregate_steps(step_results)
        return test_result


class NmslibQueryTest(Test):
    def __init__(self, service_config: NmslibConfig, dataset: tool.Dataset):
        self.service_config = service_config
        self.dataset = dataset

    def setup(self):
        result = nmslib.init_index(space=self.service_config.method.space)
        self.index = result['index']
        nmslib.bulk_index(index=self.index, dataset=self.dataset.train[:])
        nmslib.create_index(index=self.index)

    def query_vectors(self, dataset: h5py.Dataset):
        results = []

        for vec in dataset:
            k = 10
            results.append(
                nmslib.query_index(index=self.index, vector=vec, k=k))

        return results

    def execute(self):
        step_results = self.query_vectors(dataset=self.dataset.test)
        test_result = _aggregate_steps(step_results)
        return test_result
