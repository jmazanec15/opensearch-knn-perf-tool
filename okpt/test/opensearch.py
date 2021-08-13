from typing import Any, Dict, Iterable

import h5py
import numpy as np
from elasticsearch import Elasticsearch
from okpt.test.profile import label, measure


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


@label('create_index')
@measure
def create_index(es: Elasticsearch, index_name: str, index_spec: Dict[str,
                                                                      Any]):
    return es.indices.create(index=index_name, body=index_spec)


@label('disable_refresh')
@measure
def disable_refresh(es: Elasticsearch):
    return es.indices.put_settings(body={'index': {'refresh_interval': -1}})


def bulk_index(es: Elasticsearch, index_name: str,
               sections: Iterable[np.ndarray]):
    @label('bulk_add')
    def bulk(index, body):
        return es.bulk(index=index, body=body)

    results = []
    for section in sections:
        result = bulk(index_name, section)
        results.append({key: result[key] for key in ['label', 'took']})
    return results


@label('refresh_index')
@measure
def refresh_index(es: Elasticsearch, index_name: str):
    return es.indices.refresh(index=index_name)


def delete_index(es: Elasticsearch, index_name: str):
    es.indices.delete(index=index_name)


@label('query_index')
def query_index(es: Elasticsearch, index_name: str, body: Dict[str, Any]):
    return es.search(index=index_name, body=body)
