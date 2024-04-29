FROM linuxserver/blender:4.1.1

# Create the /tmp/.X11-unix directory with the appropriate permissions
RUN mkdir /tmp/.X11-unix && \
chmod 1777 /tmp/.X11-unix && \
chown root:root /tmp/.X11-unix

# Is read by the docker_entry.sh script
# used to determine if tests or exmaples should be run
ENV FUSRR_RUN_TYPE=tests

ENV HATCH_ENV_TYPE_VIRTUAL_PATH=.venv

WORKDIR /app

# Install Python 3.10
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.10 python3-pip \
    && pip install --upgrade pip hatch \
    # seems to help the Docker container to run without errors
    && pip install pyxdg

COPY docker/docker_entry.sh pyproject.toml README.md ./

COPY scripts ./scripts

COPY examples ./examples
COPY tests ./tests
COPY fusrr ./fusrr

ENTRYPOINT [ "./docker_entry.sh" ]
