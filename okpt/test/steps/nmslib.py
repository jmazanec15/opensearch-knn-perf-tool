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
import numpy as np
from okpt.io.config.parsers import nmslib as nmslib_parser
from okpt.test import profile

import nmslib


@profile.label('init_index')
@profile.took
def init_index(service_config: nmslib_parser.NmslibConfig):
    index = nmslib.init(method=service_config.method.name,
                        space=service_config.method.space_type)
    return {'index': index}


@profile.label('bulk_add')
@profile.took
def bulk_index(index: nmslib.dist.FloatIndex, dataset: np.ndarray):
    index.addDataPointBatch(data=dataset)
    return {}


@profile.label('create_index')
@profile.took
def create_index(index: nmslib.dist.FloatIndex,
                 service_config: nmslib_parser.NmslibConfig):
    index.createIndex({
        'efConstruction': service_config.method.parameters.ef_construction,
        'M': service_config.method.parameters.M,
        'indexThreadQty': service_config.method.parameters.index_thread_qty,
        'post': service_config.method.parameters.post
    })
    return {}


@profile.label('query_index')
@profile.took
def query_index(index: nmslib.dist.FloatIndex, vector: np.ndarray, k: int):
    ids, distances = index.knnQuery(vector, k=k)
    return {'ids': ids, 'distances': distances}
