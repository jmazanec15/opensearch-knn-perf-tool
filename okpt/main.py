""" Runner script that serves as the main controller of the testing tool.
"""

from okpt.io import reader, writer, parser

def main():
    reader.define_args()
    args = reader.get_args()

    if args['command'] == 'test':
        data = {'a': 1, 'b': 2, 'c': 3}
        file = args['output_path']
        config = parser.parse_yaml(args['config_path'])
        service_config_file = open(config['service_config'], 'r')
        service_config = parser.parse_json(service_config_file)

        # print(config)
        # print(service_config)

        writer.write_json(data, file)
    elif args['command'] == 'plot':
        pass # TODO
    elif args['command'] == 'compare':
        pass # TODO
