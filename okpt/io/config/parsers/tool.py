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
"""Provides ToolParser.

Classes:
    ToolParser: Tool config parser.
"""
from dataclasses import dataclass
from io import TextIOWrapper
from typing import Any, Dict, Union

import h5py
from okpt.io.config.parsers import base, utils
from okpt.io.config.parsers.nmslib import NmslibConfig
from okpt.io.config.parsers.opensearch import OpenSearchConfig
from okpt.io.utils import reader


@dataclass
class TestParameters:
    num_runs: int


@dataclass
class ToolConfig:
    test_name: str
    test_type: str
    knn_service: str
    service_config: Union[OpenSearchConfig, NmslibConfig]
    dataset: Union[h5py.File, Dict[str, Any]]
    dataset_format: str
    test_parameters: TestParameters


@dataclass
class Dataset:
    train: h5py.Dataset
    test: h5py.Dataset


def _parse_dataset(dataset_path: str,
                   dataset_format: str) -> Union[Dataset, Dict[str, Any]]:
    if dataset_format == 'hdf5':
        file = h5py.File(dataset_path)
        return Dataset(train=file['train'], test=file['test'])
    elif dataset_format == 'json':
        # TODO: support nljson instead of json for opensearch ingestion
        return reader.parse_json_from_path(dataset_path)
    else:
        raise Exception()


class ToolParser(base.BaseParser):
    """Parser for Tool config.

    Methods:
        parse: Parse and validate the Tool config.
    """
    def __init__(self):
        super().__init__('tool')

    def parse(self, file_obj: TextIOWrapper) -> ToolConfig:
        """See base class."""

        config_obj = super().parse(file_obj)

        # determine which knn_service is used
        knn_service_name = config_obj['knn_service']
        service_config_path = config_obj['service_config']
        service_config_file_obj = reader.get_file_obj(service_config_path)
        config_parser = utils.get_parser(knn_service_name)

        dataset = _parse_dataset(config_obj['dataset'],
                                 config_obj['dataset_format'])
        tool_config = ToolConfig(
            test_name=config_obj['test_name'],
            test_type=config_obj['test_type'],
            knn_service=config_obj['knn_service'],
            service_config=config_parser.parse(service_config_file_obj),
            dataset=dataset,
            dataset_format=config_obj['dataset_format'],
            test_parameters=TestParameters(
                config_obj['test_parameters']['num_runs']),
        )
        return tool_config
