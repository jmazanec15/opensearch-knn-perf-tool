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
if [[ -z $OKPT_LOG_LEVEL ]]; then
  su test -c "python3 knn-perf-tool.py $OKPT_COMMAND $OKPT_CONFIG_PATH $OKPT_OUTPUT_PATH"
else
  su test -c "python3 knn-perf-tool.py --log $OKPT_LOG_LEVEL $OKPT_COMMAND $OKPT_CONFIG_PATH $OKPT_OUTPUT_PATH"
fi
