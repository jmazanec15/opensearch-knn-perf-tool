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
"""Provides steps for OpenSearch tests.

Some of the OpenSearch operations return a `took` field in the response body,
so the profiling decorators aren't needed for some functions.
"""
from typing import Any, Dict, List, cast

import h5py
import numpy as np

from opensearchpy import OpenSearch, RequestsHttpConnection
from okpt.test.steps import base


class CreateIndexStep(base.Step):
    """See base class."""

    label = 'create_index'
    measures = ['took']

    def __init__(self, opensearch: OpenSearch, index_name: str,
                 index_spec: Dict[str, Any]):
        self.opensearch = opensearch
        self.index_name = index_name
        self.index_spec = index_spec

    def _action(self):
        """Creates an OpenSearch index, applying the index settings/mappings.

        Returns:
            An OpenSearch index creation response body.
        """
        return self.opensearch.indices.create(index=self.index_name,
                                      body=self.index_spec


class DisableRefreshStep(base.Step):
    """See base class."""

    label = 'disable_refresh'
    measures = ['took']

    def __init__(self, opensearch: OpenSearch):
        self.opensearch = opensearch

    def _action(self):
        """Disables the refresh interval for an OpenSearch index.

        Returns:
            An OpenSearch index settings update response body.
        """
        return self.opensearch.indices.put_settings(
            body={'index': {
                'refresh_interval': -1
            }})


class BulkStep(base.Step):
    """See base class."""

    label = 'bulk_add'
    measures = ['took']

    def __init__(self, opensearch: OpenSearch, index_name: str, body):
        self.opensearch = opensearch
        self.index_name = index_name
        self.body = body

    def _action(self):
        """Make bulk request to OpenSearch.

        Returns:
            An OpenSearch bulk response body.
        """
        return self.opensearch.bulk(index=self.index_name, body=self.body)

class RefreshIndexStep(base.Step):
    """See base class."""

    label = 'refresh_index'
    measures = ['took']
    def __init__(self, opensearch: OpenSearch, index_name: str):
        self.opensearch = opensearch
        self.index_name = index_name

    def _action(self):
        return self.opensearch.indices.refresh(index=self.index_name)

class QueryIndexStep(base.Step):
    """See base class."""

    label = 'query_index'
    measures = ['took']

    def __init__(self, opensearch: OpenSearch, index_name: str,
                 body: Dict[str, Any]):
        self.opensearch = opensearch
        self.index_name = index_name
        self.body = body

    def _action(self):
        """Queries a vector against an OpenSearch index.

        Returns:
            An OpenSearch query response body.
        """
        return self.opensearch.search(index=self.index_name, body=self.body)


def bulk_transform(partition: np.ndarray,
                   action=Dict[str, Any]) -> List[Dict[str, Any]]:
    """Partitions and transforms a list of vectors into OpenSearch's bulk injection format.
    Args:
        section: An array of vectors to transform.
        action: Bulk API action.
    Returns:
        An array of transformed vectors in bulk format.
    """
    actions = [action, None] * len(partition)
    actions[1::2] = [{'test_vector': vec} for vec in partition.tolist()]
    return actions


def bulk_index(opensearch: OpenSearch, index_name: str,
               dataset: h5py.Dataset, bulk_size: int):
    """Bulk indexes vectors into an OpenSearch index.
    Args:
        opensearch: An OpenSearch client.
        index_name: Name of the OpenSearch index to ingest vectors into.
        dataset: Dataset of vectors to bulk ingest.
        bulk_size: Number of vectors in one bulk request.
    Returns:
        An array of bulk injection responses.
    """
    results = []
    action = {'index': {'_index': index_name}}
    i = 0
    while i < dataset.len():
        partition = cast(np.ndarray, dataset[i:i + bulk_size])
        body = bulk_transform(partition, action)
        result = BulkStep(opensearch=opensearch, index_name=index_name, body=body).execute()
        results.append(result)
        i += bulk_size

    return results


def batch_query_index(opensearch: OpenSearch, index_name: str,
                      dataset: h5py.Dataset, k: int) -> List[Dict[str, Any]]:
    """Queries an array of vectors against an OpenSearch index.

    Args:
        opensearch: An OpenSearch client.
        index_name: Name of the OpenSearch index to be searched against.
        dataset: Array of vectors to query.
        k: Number of neighbors to search for.
    Returns:
        A list of `query_index` responses.
    """
    get_body = lambda vec, k: {
        'size': k,
        'query': {
            'knn': {
                'test_vector': {
                    'vector': vec,
                    'k': k
                }
            }
        }
    }
    return [
        QueryIndexStep(opensearch=opensearch, index_name=index_name,
                       body=get_body(v, k)).execute() for v in dataset
    ]


def delete_index(opensearch: OpenSearch, index_name: str):
    """Deletes an OpenSearch index.

    Args:
        opensearch: An OpenSearch client.
        index_name: Name of the OpenSearch index to be deleted.

    Returns:
        An OpenSearch index deletion response body.
    """
    opensearch.indices.delete(index=index_name)
