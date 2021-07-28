#!/usr/bin/env bash

# start opensearch
export OPENSEARCH_JAVA_OPTS="-Xms512m -Xmx512m" # minimum and maximum Java heap size, recommend setting both to 50% of system RAM
su opensearch -c '/usr/share/opensearch/opensearch-docker-entrypoint.sh' > output/opensearch.log &

# ping opensearch to see if it has started yet
# if it hasn't, wait 10 seconds and try again
elapsed_time=0
e=$(curl -o /dev/null -s -w "%{http_code}\n" localhost:9200)
while [[ $e != "200" ]]; do
  # exit if opensearch hasn't started in 2 minutes
  if [[ $elapsed_time -gt 120 ]]; then
    echo "OpenSearch hasn't started in 2 minutes. Aborting..."
    exit 1
  fi

  echo "Waiting for opensearch to come up. Sleeping 10 seconds... If it doesnt come up in a minute, somethings wrong."
  sleep 10
  elapsed_time=$((elapsed_time + 10))
  e=$(curl -o /dev/null -s -w "%{http_code}\n" localhost:9200)
done

# run testing tool
su test -c "python3 knn-perf-tool.py $OKPT_COMMAND $OKPT_CONFIG_PATH $OKPT_OUTPUT_PATH"
