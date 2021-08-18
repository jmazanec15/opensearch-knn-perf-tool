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
"""Provides NMSLIB Test classes."""
from okpt.test.steps import nmslib
from okpt.test.tests import base


class NmslibIndexTest(base.Test):
    """See base class. Test class for indexing against NMSLIB."""
    def _run_steps(self):
        """See base class. Initializes index, bulk indexes vectors, and creates the index."""
        result = nmslib.init_index(service_config=self.service_config)
        self.index = result['index']
        self.step_results = [
            result,
            nmslib.bulk_index(index=self.index, dataset=self.dataset.train),
            nmslib.create_index(index=self.index,
                                service_config=self.service_config)
        ]


class NmslibQueryTest(base.Test):
    """See base class. Test class for querying against NMSLIB."""
    def setup(self):
        """See base class. Sets up an NMSLIB index."""
        result = nmslib.init_index(service_config=self.service_config)
        self.index = result['index']
        nmslib.bulk_index(index=self.index, dataset=self.dataset.train)
        nmslib.create_index(index=self.index,
                            service_config=self.service_config)
        self.index.setQueryTimeParams(
            {'efSearch': self.service_config.ef_search})

    def _run_steps(self):
        """See base class. Queries vectors against an NMSLIB index."""
        self.step_results = [
            *nmslib.batch_query_index(index=self.index,
                                      dataset=self.dataset.test,
                                      k=self.service_config.k)
        ]
