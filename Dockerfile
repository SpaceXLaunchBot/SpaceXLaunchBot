FROM python:3.8-alpine

WORKDIR /opt/SpaceXLaunchBot
COPY . .

# GCC / other build tools required for pip install; https://wiki.alpinelinux.org/wiki/GCC.
RUN apk add build-base
RUN pip install -r requirements.txt

ENV INSIDE_DOCKER "True"

CMD python ./spacexlaunchbot/main.py
