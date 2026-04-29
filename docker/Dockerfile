FROM linuxserver/blender:latest

# Create the /tmp/.X11-unix directory with the appropriate permissions
RUN mkdir /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix && \
    chown root:root /tmp/.X11-unix

# This is read by the docker_entry.sh script,
# used to determine if tests or exmaples should be run
ENV FUSRR_RUN_TYPE=tests

# sets the virtual environment path for Hatch
ENV HATCH_ENV_TYPE_VIRTUAL_PATH=.venv

## -- Install Python 3.13 from uv --
FROM python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN uv python install 3.13

# -- Setup and build PROCESS --
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y git

RUN uv pip install --system "git+https://github.com/ukaea/process@v3.3.0"

# for now, we only need the python source from PROCESS
# and don't need to build it, as we don't run it.
#! do not remove - could be useful in the future
# RUN cd PROCESS && cmake -S . -B build -DRELEASE=TRUE && cmake --build build

# -- Copy in FusRR files --

WORKDIR /app

# This script is the entrypoint for the Docker container
# which will run the Hatch scripts for the examples or tests
# pyproject.toml and README.md are needed to run the Hatch shells
COPY docker/docker_entry.sh pyproject.toml README.md ./

# The main source files
COPY examples ./examples
COPY tests ./tests
COPY fusrr ./fusrr

ENTRYPOINT [ "./docker_entry.sh" ]
