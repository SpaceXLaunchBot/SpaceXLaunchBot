FROM python:3.8-slim-buster

WORKDIR /opt/SpaceXLaunchBot
COPY . .

RUN pip install -r requirements.txt
ENV INSIDE_DOCKER "True"

# -u so stdout shows up in Docker log.
CMD ["python","-u","./spacexlaunchbot/main.py"]
