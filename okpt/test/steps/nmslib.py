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
"""Provides steps for NMSLIB tests.

The profiling decorators require the wrapped functions to return an dictionary,
so the functions in this module may return a blank dictionary in order to be
profiled.
"""
from typing import Any, Dict, List

import nmslib
import numpy as np

from okpt.io.config.parsers import nmslib as nmslib_parser
from okpt.test import profile


@profile.label('init_index')
@profile.took
@profile.step
def init_index(service_config: nmslib_parser.NmslibConfig):
    """Initializes an NMSLIB index.

    Args:
        service_config: An NMSLIB config.

    Returns:
        An object with the new NMSLIB index.
    """
    index = nmslib.init(method=service_config.method.name,
                        space=service_config.method.space_type)
    return {'index': index}


@profile.label('bulk_add')
@profile.took
@profile.step
def bulk_index(index: nmslib.dist.FloatIndex, dataset: np.ndarray):
    """Bulk indexes vectors into an NMSLIB index.

    Args:
        index: An NMSLIB index.
        dataset: A numpy array of vectors to be indexed.

    Returns:
        A blank object (for profiling).
    """
    index.addDataPointBatch(data=dataset)


@profile.label('create_index')
@profile.took
@profile.step
def create_index(index: nmslib.dist.FloatIndex,
                 service_config: nmslib_parser.NmslibConfig):
    """Creates an NMSLIB index, making it available for querying.

    Args:
        index: An NMSLIB index.
        service_config: An NMSLIB config.

    Returns:
        A blank object (for profiling).
    """
    index.createIndex({
        'efConstruction': service_config.method.parameters.ef_construction,
        'M': service_config.method.parameters.m,
        'indexThreadQty': service_config.index_thread_qty,
        'post': service_config.post
    })


@profile.label('query_index')
@profile.took
@profile.step
def query_index(index: nmslib.dist.FloatIndex, vector: np.ndarray, k: int):
    """Runs a single query against an NMSLIB index.

    Args:
        index: An NMSLIB index.
        vector: A vector to query for.
        k: Number of neighbors to search for.

    Returns:
        A dictionary containing the ids and distances of the query vector's
        neighbors.
    """
    ids, distances = index.knnQuery(vector, k=k)
    return {'ids': ids, 'distances': distances}


def batch_query_index(index: nmslib.dist.FloatIndex, dataset: np.ndarray,
                      k: int) -> List[Dict[str, Any]]:
    """Runs a group of queries against an NMSLIB index.

    Args:
        index: An NMSLIB index.
        dataset: An array of vectors to query for.
        k: Number of neighbors to search for.

    Returns:
        A list of `query_index` responses.
    """
    return [query_index(index=index, vector=v, k=k) for v in dataset]
