FROM opensearchproject/opensearch

USER root
RUN yum install -y python3 pip3 util-linux
RUN useradd -ms /bin/bash test

USER opensearch
ADD --chown=opensearch config/opensearch.yml /usr/share/opensearch/config/opensearch.yml

USER test
WORKDIR /home/test
ADD --chown=test requirements.txt .
RUN pip3 install -r requirements.txt --user
ADD --chown=test okpt okpt
ADD --chown=test scripts scripts
ADD --chown=test knn-perf-tool.py .
RUN chmod -R u+x scripts

USER root
CMD scripts/opensearch-entrypoint.sh
