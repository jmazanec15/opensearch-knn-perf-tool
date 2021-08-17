from okpt.io.config.parsers import nmslib as nmslib_parser
from okpt.io.config.parsers import tool
from okpt.test.steps import nmslib
from okpt.test.tests import base


class NmslibIndexTest(base.Test):
    def __init__(self, service_config: nmslib_parser.NmslibConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.dataset = dataset

    def run_steps(self):
        result = nmslib.init_index(service_config=self.service_config)
        self.index = result['index']
        self.step_results += [
            result,
            nmslib.bulk_index(index=self.index, dataset=self.dataset.train),
            nmslib.create_index(index=self.index,
                                service_config=self.service_config)
        ]


class NmslibQueryTest(base.Test):
    def __init__(self, service_config: nmslib_parser.NmslibConfig,
                 dataset: tool.Dataset):
        super().__init__(service_config, dataset)

        self.dataset = dataset

    def setup(self):
        result = nmslib.init_index(service_config=self.service_config)
        self.index = result['index']
        nmslib.bulk_index(index=self.index, dataset=self.dataset.train)
        nmslib.create_index(index=self.index,
                            service_config=self.service_config)

    def run_steps(self):
        self.index.setQueryTimeParams(
            {'efSearch': self.service_config.method.parameters.ef_search})
        for vec in self.dataset.test:
            k = 10
            result = nmslib.query_index(index=self.index, vector=vec, k=k)
            self.step_results.append(result)
