FROM python:3.9-slim-buster

WORKDIR /SpaceXLaunchBot
COPY . .

ENV INSIDE_DOCKER "True"
RUN python setup.py install

HEALTHCHECK CMD discordhealthcheck || exit 1

# We use ENTRYPOINT so it will recieve signals (https://stackoverflow.com/a/64960372/6396652).
ENTRYPOINT ["spacexlaunchbot"]
