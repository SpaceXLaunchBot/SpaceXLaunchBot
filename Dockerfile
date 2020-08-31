FROM python:3.8-slim-buster

WORKDIR /SpaceXLaunchBot
COPY . .

ENV INSIDE_DOCKER "True"
RUN python setup.py install

# https://github.com/krallin/tini#using-tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

HEALTHCHECK CMD discordhealthcheck || exit 1
CMD ["spacexlaunchbot"]

# docker run -d --name spacexlaunchbot \
#     -v /path/to/dir:/docker-volume \
#     --env-file /path/to/variables.env \
#     psidex/spacexlaunchbot
