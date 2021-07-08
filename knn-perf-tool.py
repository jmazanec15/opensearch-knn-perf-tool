""" Runner script that serves as the entrypoint to the knn-perf-tool.
"""

from okpt.io import reader, writer

reader.define_args()
args = reader.get_args()
print(args)


data = {'a': 1, 'b': 2, 'c': 3}
writer.write_json(data, args['output_path'])
