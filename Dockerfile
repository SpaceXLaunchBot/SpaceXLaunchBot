FROM python:3.13-slim-trixie
ENV PYTHONUNBUFFERED=True

WORKDIR /SpaceXLaunchBot

# https://rdrn.me/postmodern-python/
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

COPY . .
RUN printf "HASH = \"$(cat ./.git/refs/heads/master)\"\nSHORT_HASH = \"$(head -c 7 ./.git/refs/heads/master)\"\n" > ./spacexlaunchbot/version.py
ENV INSIDE_DOCKER="True"

HEALTHCHECK --interval=5m --timeout=10s \
  CMD discordhealthcheck || exit 1

# ENTRYPOINT so it will recieve signals - https://stackoverflow.com/a/64960372/6396652
ENTRYPOINT ["/SpaceXLaunchBot/.venv/bin/python", "-m", "spacexlaunchbot"]
