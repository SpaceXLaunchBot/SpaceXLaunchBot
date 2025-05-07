FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install gcc -y

WORKDIR /SpaceXLaunchBot
COPY . .

RUN printf "HASH = \"$(cat ./.git/refs/heads/master)\"\nSHORT_HASH = \"$(head -c 7 ./.git/refs/heads/master)\"\n" > ./spacexlaunchbot/version.py

ENV INSIDE_DOCKER="True"

# TODO: Migrate to modern Python tooling
RUN pip install setuptools
RUN pip install -r requirements.txt
RUN python setup.py install

HEALTHCHECK --interval=5m --timeout=10s \
  CMD discordhealthcheck || exit 1

# ENTRYPOINT so it will recieve signals - https://stackoverflow.com/a/64960372/6396652
ENTRYPOINT ["spacexlaunchbot"]
