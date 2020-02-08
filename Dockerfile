FROM python:3.8-alpine

WORKDIR /opt/SpaceXLaunchBot
COPY . .

ENV INSIDE_DOCKER "True"

# GCC / other build tools required for pip install; https://wiki.alpinelinux.org/wiki/GCC.
RUN apk add build-base
RUN pip install -r requirements.txt

# -u so stdout shows up in Docker log.
CMD ["python","-u","./spacexlaunchbot/main.py"]
