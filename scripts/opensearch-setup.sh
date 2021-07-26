#!/usr/bin/env bash

e=$(curl -o /dev/null -s -w "%{http_code}\n" localhost:9200)
while [[ $e != "200" ]]; do
  echo "Waiting for opensearch to come up...Sleeping 10 seconds.. If it doesnt come up in a minute, somethings wrong"
  sleep 10
  e=$(curl -o /dev/null -s -w "%{http_code}\n" localhost:9200)
done
