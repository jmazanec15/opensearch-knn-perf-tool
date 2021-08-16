from elasticsearch import Elasticsearch, RequestsHttpConnection
from okpt.io.config.parsers import opensearch as opensearch_parser
from okpt.io.config.parsers import tool
from okpt.test.steps import opensearch
from okpt.test.tests import base


class OpenSearchTest(base.Test):
    def __init__(self, service_config: opensearch_parser.OpenSearchConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.index_name = 'test_index'
        self.es = Elasticsearch(hosts=[{
            'host': 'localhost',
            'port': 9200
        }],
                                use_ssl=False,
                                verify_certs=False,
                                connection_class=RequestsHttpConnection,
                                timeout=60)

    def setup(self):
        body = {
            'transient': {
                'knn.algo_param.index_thread_qty':
                self.service_config.index_thread
            }
        }
        self.es.cluster.put_settings(body=body)


class OpenSearchIndexTest(OpenSearchTest):
    def __init__(self, service_config: opensearch_parser.OpenSearchConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.action = {'index': {'_index': self.index_name}}

    def setup(self):
        super().setup()

        # split training set into sections for bulk ingestion
        self.sections = opensearch.bulk_transform_vectors(
            self.dataset.train, self.action, self.bulk_size)

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
    def __init__(self, service_config: opensearch_parser.OpenSearchConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.action = {'index': {'_index': self.index_name}}

    def setup(self):
        super().setup()

        self.sections = opensearch.bulk_transform_vectors(
            self.dataset.train, self.action, self.bulk_size)
        opensearch.create_index(self.es, self.index_name,
                                self.service_config.index_spec)
        opensearch.bulk_index(self.es, self.index_name, self.sections)
        opensearch.refresh_index(self.es, self.index_name)

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
