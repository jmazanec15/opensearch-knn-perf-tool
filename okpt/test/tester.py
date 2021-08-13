from okpt.io.config.parsers.base import ConfigurationError
from okpt.io.config.parsers.tool import ToolConfig
from okpt.test import test


def _get_test(test_id: int):
    if test_id == 1:
        return test.OpenSearchIndexTest
    elif test_id == 2:
        return test.OpenSearchQueryTest
    elif test_id == 3:
        return test.NmslibIndexTest
    elif test_id == 4:
        return test.NmslibQueryTest
    else:
        raise ConfigurationError(message='Invalid test_id.')


class Tester():
    def __init__(self, tool_config: ToolConfig):
        self.tool_config = tool_config
        self.test = _get_test(tool_config.test_id)(
            service_config=tool_config.service_config,
            dataset=tool_config.dataset)
        self.test.setup()

    def execute(self):
        return self.test.execute()
