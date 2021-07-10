from io import TextIOWrapper
import os

import cerberus

from okpt.io import reader
from okpt.io.config import parser

SCHEMAS_DIR = os.path.dirname(os.path.abspath(__file__)) + '/schemas'
SCHEMAS = ['tool', 'opensearch', 'nmslib']

schema_paths = {
    schema: os.path.join(SCHEMAS_DIR, schema + '.yml')
    for schema in SCHEMAS
}
schema_files = {
    schema: reader.get_read_file(path)
    for schema, path in schema_paths.items()
}
schema_objs = {
    schema: parser.parse_yaml(file)
    for schema, file in schema_files.items()
}
schema_validators = {
    schema: cerberus.Validator(obj)
    for schema, obj in schema_objs.items()
}


def validate(tool_config: TextIOWrapper) -> bool:

    # validate tool config
    tool_config_obj = parser.parse_yaml(tool_config)
    is_tool_config_valid = schema_validators['tool'].validate(tool_config_obj)

    if (not is_tool_config_valid):
        print('exception raised')
        # TODO: Add custom exception
        raise Exception(schema_validators['tool'].errors)

    # validate service config
    knn_service = tool_config_obj['knn_service']
    service_config_path = tool_config_obj['service_config']
    service_config_file = reader.get_read_file(service_config_path)
    service_config_obj = parser.parse_yaml(service_config_file)
    is_service_config_valid = schema_validators[knn_service].validate(
        service_config_obj)

    if (not is_service_config_valid):
        raise Exception(schema_validators[knn_service].errors)

    return True
