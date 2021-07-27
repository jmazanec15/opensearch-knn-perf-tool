FROM amazonlinux:latest
WORKDIR /app

RUN yum install -y python3 pip3 util-linux
RUN useradd -ms /bin/bash test

USER test
WORKDIR /home/test
ADD --chown=test requirements.txt .
RUN pip3 install -r requirements.txt
ADD --chown=test okpt okpt
ADD --chown=test scripts scripts
ADD --chown=test knn-perf-tool.py .
RUN chmod -R u+x scripts

CMD scripts/nmslib-entrypoint.sh
