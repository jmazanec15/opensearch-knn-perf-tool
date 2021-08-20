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
from typing import Any, Dict, List

import elasticsearch
import h5py
import numpy as np

from okpt.test import profile


@profile.label('create_index')
@profile.took
@profile.step
def create_index(es: elasticsearch.Elasticsearch, index_name: str,
                 index_spec: Dict[str, Any]):
    """Creates an OpenSearch index, applying the index settings/mappings.

    Args:
        es: An OpenSearch client.
        index_name: Name of the OpenSearch index.
        index_spec: Dictionary containing the index settings/mappings.

    Returns:
        An OpenSearch index creation response body.
    """
    return es.indices.create(index=index_name, body=index_spec)


@profile.label('disable_refresh')
@profile.took
@profile.step
def disable_refresh(es: elasticsearch.Elasticsearch):
    """Disables the refresh interval for an OpenSearch index.

    Args:
        es: An OpenSearch client.

    Returns:
        An OpenSearch index settings update response body.
    """
    return es.indices.put_settings(body={'index': {'refresh_interval': -1}})


def bulk_transform(partition: np.ndarray,
                   action=Dict[str, Any]) -> List[Dict[str, Any]]:
    """Partitions and transforms a list of vectors into OpenSearch's bulk injection format.

    Args:
        section: An array of vectors to transform.
        action: Bulk API action

    Returns:
        An array of transformed vectors in bulk format.
    """
    actions = [action, None] * len(partition)
    actions[1::2] = [{'test_vector': vec} for vec in partition.tolist()]
    return actions


@profile.label('bulk_add')
@profile.step
def bulk(es: elasticsearch.Elasticsearch, index_name: str, body):
    """Make bulk request to Elasticsearch.

    Args:
        es: An OpenSearch client.
        index_name: Name of Elasticsearch index
        body: Bulk request body

    Returns:
        Elasticsearch bulk response body.
    """
    return es.bulk(index=index_name, body=body)


def bulk_index(es: elasticsearch.Elasticsearch, index_name: str,
               dataset: h5py.Dataset, bulk_size: int):
    """Bulk indexes vectors into an Elasticsearch index.

    Args:
        es: An OpenSearch client.
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
        partition = dataset[i:i + bulk_size]
        body = bulk_transform(partition, action)
        result = bulk(es=es, index_name=index_name, body=body)
        results.append(result)
        i += bulk_size

    return results


@profile.label('refresh_index')
@profile.took
@profile.step
def refresh_index(es: elasticsearch.Elasticsearch, index_name: str):
    """Refreshes an OpenSearch index, making it available for searching.

    Args:
        es: An OpenSearch client.
        index_name: Name of the OpenSearch index to be refreshed.

    Returns:
        An OpenSearch index refresh response body.
    """
    return es.indices.refresh(index=index_name)


def delete_index(es: elasticsearch.Elasticsearch, index_name: str):
    """Deletes an OpenSearch index.

    Args:
        es: An OpenSearch client.
        index_name: Name of the OpenSearch index to be deleted.

    Returns:
        An OpenSearch index deletion response body.
    """
    es.indices.delete(index=index_name)


@profile.label('query_index')
@profile.step
def query_index(es: elasticsearch.Elasticsearch, index_name: str,
                body: Dict[str, Any]):
    """Queries a vector against an OpenSearch index.

    Args:
        es: An OpenSearch client.
        index_name: Name of the OpenSearch index to be searched against.
        body: A dictionary containing the body of the search request.

    Returns:
        An OpenSearch query response body.
    """
    return es.search(index=index_name, body=body)


def batch_query_index(es: elasticsearch.Elasticsearch, index_name: str,
                      dataset: h5py.Dataset, k: int) -> List[Dict[str, Any]]:
    """Queries an array of vectors against an OpenSearch index.

    Args:
        es: An OpenSearch client.
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
        query_index(es=es, index_name=index_name, body=get_body(v, k))
        for v in dataset
    ]
