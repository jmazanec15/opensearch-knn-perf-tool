import numpy as np
from okpt.io.config.parsers import nmslib as nmslib_parser
from okpt.test.profile import label, measure

import nmslib


@label('init_index')
@measure
def init_index(service_config: nmslib_parser.NmslibConfig):
    index = nmslib.init(method=service_config.method.name,
                        space=service_config.method.space_type)
    return {'index': index}


@label('bulk_add')
@measure
def bulk_index(index: nmslib.dist.FloatIndex, dataset: np.ndarray):
    index.addDataPointBatch(data=dataset)
    return {}


@label('create_index')
@measure
def create_index(index: nmslib.dist.FloatIndex,
                 service_config: nmslib_parser.NmslibConfig):
    index.createIndex({
        'efConstruction': service_config.method.parameters.ef_construction,
        'M': service_config.method.parameters.M,
        'indexThreadQty': service_config.method.parameters.index_thread_qty,
        'post': service_config.method.parameters.post
    })
    return {}


@label('query_index')
@measure
def query_index(index: nmslib.dist.FloatIndex, vector: np.ndarray, k: int):
    ids, distances = index.knnQuery(vector, k=k)
    return {'ids': ids, 'distances': distances}
