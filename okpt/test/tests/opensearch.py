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
"""Provides OpenSearch Test classes."""
from elasticsearch import Elasticsearch, RequestsHttpConnection

from okpt.io.config.parsers import opensearch as opensearch_parser
from okpt.io.config.parsers import tool
from okpt.test.steps import opensearch
from okpt.test.tests import base


class OpenSearchTest(base.Test):
    """See base class. Base OpenSearch Test class."""

    def __init__(self, service_config: opensearch_parser.OpenSearchConfig,
                 dataset: tool.Dataset):
        """See base class. Initializes the OpenSearch client."""
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
        """See base class. Initializes cluster settings and transforms dataset in bulk ingestion format."""
        body = {
            'transient': {
                'knn.algo_param.index_thread_qty':
                    self.service_config.index_thread_qty
            }
        }
        self.es.cluster.put_settings(body=body)

    def _cleanup(self):
        """See base class. Deletes the OpenSearch index."""
        opensearch.delete_index(es=self.es, index_name=self.index_name)


class OpenSearchIndexTest(OpenSearchTest):
    """See base class. Test class for indexing against OpenSearch."""

    def _run_steps(self):
        """See base class. Creates index, bulk indexes vectors, and refreshes the index."""
        self.step_results = [
            opensearch.create_index(self.es, self.index_name,
                                    self.service_config.index_spec),
            *opensearch.bulk_index(self.es, self.index_name, self.dataset.train,
                                   self.service_config.bulk_size),
            opensearch.refresh_index(self.es, self.index_name)
        ]


class OpenSearchQueryTest(OpenSearchTest):
    """See base class. Test class for querying against OpenSearch."""

    def setup(self):
        """See base class. Sets up an OpenSearch index."""
        super().setup()

        opensearch.create_index(self.es, self.index_name,
                                self.service_config.index_spec)
        opensearch.bulk_index(self.es, self.index_name, self.dataset.train,
                              self.service_config.bulk_size)
        opensearch.refresh_index(self.es, self.index_name)

    def _run_steps(self):
        """See base class. Queries vectors against an OpenSearch index."""
        self.step_results = [
            *opensearch.batch_query_index(es=self.es,
                                          index_name=self.index_name,
                                          dataset=self.dataset.test,
                                          k=self.service_config.k)
        ]

    def _cleanup(self):
        pass
