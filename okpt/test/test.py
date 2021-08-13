import json
import logging
from typing import Any, Dict, List

import h5py
import nmslib
from elasticsearch import Elasticsearch, RequestsHttpConnection
from okpt.io.config.parsers.nmslib import NmslibConfig
from okpt.io.config.parsers.opensearch import OpenSearchConfig
from okpt.io.config.parsers.tool import Dataset
from okpt.test.opensearch import (bulk_index, bulk_transform_vectors,
                                  create_index, delete_index, disable_refresh,
                                  query_index, refresh_index)


def aggregate_steps(steps: List[Dict[str, Any]]):
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
        self.index_spec = service_config.index_spec
        self.es = Elasticsearch(hosts=[{
            'host': 'localhost',
            'port': 9200
        }],
                                use_ssl=False,
                                verify_certs=False,
                                connection_class=RequestsHttpConnection)

    def setup(self):
        body = {
            'knn.algo_param.index_thread_qty': self.service_config.index_thread
        }
        self.es.cluster.put_settings(body=body)

    def execute(self):
        pass


class OpenSearchIndexTest(OpenSearchTest):
    def __init__(self, service_config: OpenSearchConfig, dataset: Dataset):
        super().__init__(service_config)
        self.dataset = dataset
        self.action = {'index': {'_index': self.index_name}}

        # split training set into sections for bulk ingestion
        bulk_size = 5000
        self.sections = bulk_transform_vectors(self.dataset.train, self.action,
                                               bulk_size)

    def setup(self):
        pass

    def index_vectors(self):
        results = []

        results.append(create_index(self.es, self.index_name, self.index_spec))
        results += bulk_index(self.es, self.index_name, self.sections)
        results.append(refresh_index(self.es, self.index_name))

        return results

    def cleanup(self):
        delete_index(es=self.es, index_name=self.index_name)

    def execute(self):
        step_results = self.index_vectors()
        test_result = aggregate_steps(step_results)
        # logging.info(self.es.cat.indices(index=self.index_name, v=True))
        # logging.info(
        #     json.dumps(self.es.indices.get(self.index_name), indent=2) + '\n')
        # logging.info(
        #     json.dumps(self.es.indices.stats(index=self.index_name), indent=2))
        self.cleanup()
        return test_result


class OpenSearchQueryTest(OpenSearchTest):
    def __init__(self, service_config: OpenSearchConfig, dataset: Dataset):
        super().__init__(service_config)
        self.dataset = dataset
        self.action = {'index': {'_index': self.index_name}}

        # split training set into sections for bulk ingestion
        bulk_size = 5000
        self.sections = bulk_transform_vectors(self.dataset.train, self.action,
                                               bulk_size)

        create_index(self.es, self.index_name, self.index_spec)
        bulk_index(self.es, self.index_name, self.sections)

    def query_vectors(self, dataset: h5py.Dataset):
        results = []

        for vec in dataset[:10]:
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
            result = query_index(es=self.es,
                                 index_name=self.index_name,
                                 body=body)
            results.append(result)

        return results

    def cleanup(self):
        delete_index(es=self.es, index_name=self.index_name)

    def execute(self):
        step_results = self.query_vectors(self.dataset.test)
        test_result = aggregate_steps(step_results)
        # logging.info(
        #     json.dumps(self.es.indices.stats(index=self.index_name), indent=2))
        self.cleanup()
        return test_result


class NmslibTest(Test):
    def __init__(self, service_config: NmslibConfig):
        self.nmslib = nmslib.init(method='hnsw',
                                  space=service_config.method.space)

    def setup(self):
        pass

    def execute(self):
        pass
