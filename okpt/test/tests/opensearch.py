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
