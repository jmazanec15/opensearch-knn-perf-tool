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
from typing import Any, Dict, List, cast
import h5py

import nmslib
import numpy as np

from okpt.io.config.parsers import nmslib as nmslib_parser
from okpt.test.steps import base


class InitIndexStep(base.Step):
    """See base class."""

    label = 'init_index'
    measures = ['took']

    def __init__(self, service_config: nmslib_parser.NmslibConfig):
        self.service_config = service_config

    def _action(self):
        """Initializes an NMSLIB index.

        Returns:
            Dict with the newly created NMSLIB index.
        """
        index = nmslib.init(method=self.service_config.method.name,
                            space=self.service_config.method.space_type)
        return {'index': index}


class BulkIndexStep(base.Step):
    """See base class."""

    label = 'bulk_add'
    measures = ['took']

    def __init__(self, index: nmslib.dist.FloatIndex, dataset: h5py.Dataset):
        self.index = index
        self.dataset = dataset

    def _action(self):
        """Bulk indexes vectors into an NMSLIB index."""
        self.index.addDataPointBatch(data=self.dataset)


class CreateIndexStep(base.Step):
    """See base class."""

    label = 'create_index'
    measures = ['took']

    def __init__(self, index: nmslib.dist.FloatIndex,
                 service_config: nmslib_parser.NmslibConfig):
        self.index = index
        self.service_config = service_config

    def _action(self):
        """Creates an NMSLIB index, making it available for querying."""
        self.index.createIndex({
            'efConstruction':
                self.service_config.method.parameters.ef_construction,
            'M':
                self.service_config.method.parameters.m,
            'indexThreadQty':
                self.service_config.index_thread_qty,
            'post':
                self.service_config.method.parameters.post
        })


class QueryIndexStep(base.Step):
    """See base class."""

    label = 'query_index'
    measures = ['took']

    def __init__(self, index: nmslib.dist.FloatIndex, vector: np.ndarray,
                 k: int):
        self.index = index
        self.vector = vector
        self.k = k

    def _action(self):
        """Runs a single query against an NMSLIB index.

        Returns:
            Dict of ids and distances of query results.
        """
        ids, distances = self.index.knnQuery(self.vector, k=self.k)
        return {'ids': ids, 'distances': distances}


def batch_query_index(index: nmslib.dist.FloatIndex, dataset: h5py.Dataset,
                      k: int) -> List[Dict[str, Any]]:
    """Runs a group of queries against an NMSLIB index.

    Args:
        index: An NMSLIB index.
        dataset: An array of vectors to query for.
        k: Number of neighbors to search for.

    Returns:
        A list of `query_index` responses.
    """
    return [
        QueryIndexStep(index=index, vector=cast(np.ndarray, v), k=k).execute()
        for v in dataset
    ]
