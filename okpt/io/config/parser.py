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
"""Provides validation for various config files.

Functions:
    validate(): Validate the tool configuration.

Exceptions:
    ConfigurationError: An error in the tool configuration.
"""

import os
from io import TextIOWrapper
from typing import Any, Dict, List

import cerberus

from okpt.io.utils import reader, parser

_TOOL, _OPENSEARCH = ['tool', 'opensearch']


class ConfigurationError(Exception):
    """Exception raised for errors in the tool configuration.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message: str):
        super().__init__()
        self.message = message


class _Validator():
    """Validator for various configuration schemas.

    Attributes:
        validator: Cerberus validator for a particular schema
        errors: Cerberus validation errors (if any are found during validation)
    """
    def __init__(self, schema_name: str):
        self.validator = self._get_validator_from_schema_name(schema_name)
        self.errors = ''

    def _get_validator_from_schema_name(self, schema_name: str):
        """Get the corresponding Cerberus validator from a schema name."""
        curr_file_dir = os.path.dirname(os.path.abspath(__file__))
        schemas_dir = os.path.join(curr_file_dir, 'schemas')
        schema_file_path = os.path.join(schemas_dir, f'{schema_name}.yml')
        schema_file_obj = reader.get_read_file_obj(schema_file_path)
        schema_obj = parser.parse_yaml(schema_file_obj)
        return cerberus.Validator(schema_obj)

    def validate(self, config_obj: Dict[str, Any]):
        """Validate the configuration obj against the class schema."""
        if not self.validator.validate(config_obj):
            self.errors = self.validator.errors
            return False
        return True


def validate(tool_config_file_obj: TextIOWrapper) -> List[Any]:
    """Validate the configurations of the tool.

    Args:
        tool_config_file_obj: File object of the tool configuration file.

    Returns:
        List with the tool configuration, service configuration, and index settings (if possible).

    Raises:
        ConfigurationError: If there is an error in the user configuration.
    """

    # validate tool config
    tool_config_validator = _Validator(_TOOL)
    tool_config_obj = parser.parse_yaml(tool_config_file_obj)
    is_tool_config_valid = tool_config_validator.validate(tool_config_obj)

    if not is_tool_config_valid:
        raise ConfigurationError(
            f'Tool Config Error: {tool_config_validator.errors}')

    # validate service config
    knn_service = tool_config_obj['knn_service']
    service_config_validator = _Validator(knn_service)
    service_config_file_path = tool_config_obj['service_config']
    service_config_obj = parser.parse_yaml_from_path(
        service_config_file_path)
    is_service_config_valid = service_config_validator.validate(
        service_config_obj)

    if not is_service_config_valid:
        raise ConfigurationError(
            f'Service Config Error: {service_config_validator.errors}')

    # check if index spec needs to be parsed (for opensearch only)
    if knn_service == _OPENSEARCH:
        index_spec_file_path = service_config_obj['index_spec']
        index_spec_obj = parser.parse_json_from_path(
            index_spec_file_path)
        return [tool_config_obj, service_config_obj, index_spec_obj]
    return [tool_config_obj, service_config_obj]
