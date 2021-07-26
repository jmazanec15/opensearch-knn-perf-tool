#!/usr/bin/env bash

export OPENSEARCH_JAVA_OPTS="-Xms512m -Xmx512m" # minimum and maximum Java heap size, recommend setting both to 50% of system RAM

# start opensearch
su opensearch -c '/usr/share/opensearch/opensearch-docker-entrypoint.sh' > output/opensearch.log &
su test -c 'scripts/opensearch-setup.sh'
su test -c 'python3 knn-perf-tool.py $OKPT_COMMAND $OKPT_CONFIG_PATH $OKPT_OUTPUT_PATH'
