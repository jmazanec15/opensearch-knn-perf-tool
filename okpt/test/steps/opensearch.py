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
from typing import Any, Dict, Iterable, List

import elasticsearch
import numpy as np

from okpt.test import profile


def bulk_partition_vectors(dataset: np.ndarray, split_size: int):
    """Partitions an array of vectors into sections for bulk ingestion.

    Partitions are formed by taking the first `n` vectors, then the next `n`,
    and so on, until all the vectors have been assigned a partition group. The
    last partition group may have less than `n` vectors.

    Args:
        dataset: Array of vectors to partition.
        split_size: Size of each partition.

    Returns:
        An array of vector partitions.
    """
    splits = list(range(split_size, len(dataset), split_size))
    return np.split(dataset[:], splits)


def bulk_transform_vectors(dataset: np.ndarray, action: Dict[str, Any],
                           bulk_size: int):
    """Partitions and transforms a list of vectors into OpenSearch's bulk injection format.

    Args:
        dataset: An array of vectors to partition and transform.
        action: The bulk action for each vector.
        bulk_size: Number of vectors in a single bulk request.
    Returns:
        An array of partitioned and transformed vectors in bulk format.
    """
    def bulk_transform(section: np.ndarray):
        """Helper function to transform vectors.

        Args:
            section: An array of vectors to transform.

        Returns:
            An array of transformed vectors in bulk format.
        """
        actions = [action, None] * len(section)
        actions[1::2] = [{'test_vector': vec} for vec in section.tolist()]
        return actions

    partitions = bulk_partition_vectors(dataset, bulk_size)
    partitions = map(bulk_transform, partitions)
    return partitions


@profile.label('create_index')
@profile.took
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
def disable_refresh(es: elasticsearch.Elasticsearch):
    """Disables the refresh interval for an OpenSearch index.

    Args:
        es: An OpenSearch client.

    Returns:
        An OpenSearch index settings update response body.
    """
    return es.indices.put_settings(body={'index': {'refresh_interval': -1}})


def bulk_index(es: elasticsearch.Elasticsearch, index_name: str,
               partitions: Iterable[np.ndarray]):
    """Creates an OpenSearch index, applying the index settings/mappings.

    Args:
        es: An OpenSearch client.
        index_name: Name of the OpenSearch index to be indexed against.
        partitions: An array of vector partitions to be indexed.

    Returns:
        An array of bulk injection responses.
    """
    @profile.label('bulk_add')
    def bulk(index, body):
        return es.bulk(index=index, body=body)

    results = []
    for partition in partitions:
        result = bulk(index_name, partition)
        results.append(result)
    return results


@profile.label('refresh_index')
@profile.took
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
                      dataset: np.ndarray, k: int) -> List[Dict[str, Any]]:
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
