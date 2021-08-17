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
from typing import Any, Dict, Iterable

import elasticsearch
import h5py
import numpy as np
from okpt.test import profile


def bulk_partition_vectors(dataset: h5py.Dataset, split_size: int):
    splits = list(range(split_size, len(dataset), split_size))
    return np.split(dataset[:], splits)


def bulk_transform_vectors(dataset: h5py.Dataset, action: Dict[str, Any],
                           bulk_size: int):
    def bulk_transform(section: np.ndarray):
        actions = [action, None] * len(section)
        actions[1::2] = [{'test_vector': vec} for vec in section.tolist()]
        return actions

    sections = bulk_partition_vectors(dataset, bulk_size)
    sections = map(bulk_transform, sections)
    return sections


@profile.label('create_index')
@profile.took
def create_index(es: elasticsearch.Elasticsearch, index_name: str,
                 index_spec: Dict[str, Any]):
    return es.indices.create(index=index_name, body=index_spec)


@profile.label('disable_refresh')
@profile.took
def disable_refresh(es: elasticsearch.Elasticsearch):
    return es.indices.put_settings(body={'index': {'refresh_interval': -1}})


def bulk_index(es: elasticsearch.Elasticsearch, index_name: str,
               sections: Iterable[np.ndarray]):
    @profile.label('bulk_add')
    def bulk(index, body):
        return es.bulk(index=index, body=body)

    results = []
    for section in sections:
        result = bulk(index_name, section)
        results.append({key: result[key] for key in ['label', 'took']})
    return results


@profile.label('refresh_index')
@profile.took
def refresh_index(es: elasticsearch.Elasticsearch, index_name: str):
    return es.indices.refresh(index=index_name)


def delete_index(es: elasticsearch.Elasticsearch, index_name: str):
    es.indices.delete(index=index_name)


@profile.label('query_index')
def query_index(es: elasticsearch.Elasticsearch, index_name: str,
                body: Dict[str, Any]):
    return es.search(index=index_name, body=body)
