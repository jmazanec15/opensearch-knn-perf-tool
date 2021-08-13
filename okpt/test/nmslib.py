import numpy as np
from okpt.test.profile import label, measure

import nmslib


@label('init_index')
@measure
def init_index(space: str):
    index = nmslib.init(space=space)
    return {'index': index}


@label('bulk_add')
@measure
def bulk_index(index: nmslib.dist.FloatIndex, dataset: np.ndarray):
    index.addDataPointBatch(data=dataset)
    return {}


@label('create_index')
@measure
def create_index(index: nmslib.dist.FloatIndex):
    index.createIndex()
    return {}


@label('query_index')
@measure
def query_index(index: nmslib.dist.FloatIndex, vector: np.ndarray, k: int):
    ids, distances = index.knnQuery(vector, k=k)
    return {'ids': ids, 'distances': distances}
