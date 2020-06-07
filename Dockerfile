FROM python:3.8-slim-buster

WORKDIR /SpaceXLaunchBot
COPY . .

ENV INSIDE_DOCKER "True"
RUN python setup.py install

HEALTHCHECK CMD discordhealthcheck || exit 1
CMD spacexlaunchbot

# docker run -d --name spacexlaunchbot \
#     -v /path/to/dir:/docker-volume \
#     --env-file /path/to/variables.env \
#     psidex/spacexlaunchbot
