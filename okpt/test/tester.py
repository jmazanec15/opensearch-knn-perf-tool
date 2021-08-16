import dataclasses
import platform
import sys
from datetime import datetime
from typing import Any, Dict, List

import psutil
from okpt.io.config.parsers.base import ConfigurationError
from okpt.io.config.parsers.tool import ToolConfig
from okpt.test.tests import nmslib, opensearch


def _get_test(test_id: int):
    if test_id == 1:
        return opensearch.OpenSearchIndexTest
    elif test_id == 2:
        return opensearch.OpenSearchQueryTest
    elif test_id == 3:
        return nmslib.NmslibIndexTest
    elif test_id == 4:
        return nmslib.NmslibQueryTest
    else:
        raise ConfigurationError(message='Invalid test_id.')


def _aggregate_tests(results: List[Dict[Any, Any]], num_runs: int):
    aggregate = {}
    for result in results:
        for key in result:
            if key in aggregate:
                aggregate[key] += result[key]
            else:
                aggregate[key] = result[key]

    aggregate = {key: aggregate[key] / num_runs for key in aggregate}
    return aggregate


class Tester():
    def __init__(self, tool_config: ToolConfig):
        self.tool_config = tool_config
        self.Test = _get_test(tool_config.test_id)

    def _add_metadata(self, obj: Dict[Any, Any]):
        svmem = psutil.virtual_memory()
        metadata = {
            'test_name':
            self.tool_config.test_name,
            'test_id':
            self.tool_config.test_id,
            'date':
            datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
            'python_version':
            sys.version,
            'os_version':
            platform.platform(),
            'processor':
            platform.processor() + ', ' + str(psutil.cpu_count(logical=True)) +
            ' cores',
            'memory':
            str(svmem.used) + ' (used) / ' + str(svmem.available) +
            ' (available) / ' + str(svmem.total) + ' (total)',
        }
        return {**metadata, **obj}

    def execute(self):
        runs = []
        for i in range(self.tool_config.test_parameters.num_runs):
            self.test = self.Test(
                service_config=self.tool_config.service_config,
                dataset=self.tool_config.dataset)
            self.test.setup()
            run = self.test.execute()
            runs.append(run)

        aggregate = _aggregate_tests(runs,
                                     self.tool_config.test_parameters.num_runs)
        full_result = self._add_metadata({
            'aggregate':
            aggregate,
            'test_parameters':
            dataclasses.asdict(self.tool_config.test_parameters)
        })
        if self.tool_config.test_parameters.show_runs:
            full_result['runs'] = runs
        return full_result
