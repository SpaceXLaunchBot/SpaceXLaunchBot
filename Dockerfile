FROM python:3.9-slim-buster

WORKDIR /SpaceXLaunchBot
COPY . .

RUN printf "HASH = \"$(cat ./.git/refs/heads/master)\"\nSHORT_HASH = \"$(head -c 7 ./.git/refs/heads/master)\"\n" > ./spacexlaunchbot/version.py

ENV INSIDE_DOCKER "True"
# nasty hack while we wait for discord.py 2.0 release
RUN apt-get update && apt-get install -y git
RUN pip install git+https://github.com/Rapptz/discord.py@master && python setup.py install

# HEALTHCHECK CMD discordhealthcheck || exit 1

# We use ENTRYPOINT so it will recieve signals (https://stackoverflow.com/a/64960372/6396652).
ENTRYPOINT ["spacexlaunchbot"]
