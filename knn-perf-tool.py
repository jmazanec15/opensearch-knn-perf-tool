""" Runner script that serves as the entrypoint to the knn-perf-tool.
"""

from okpt.io import reader, writer

reader.define_args()
args = reader.get_args()
print(args)
