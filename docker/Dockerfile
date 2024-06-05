FROM linuxserver/blender:4.1.1

# Create the /tmp/.X11-unix directory with the appropriate permissions
RUN mkdir /tmp/.X11-unix && \
    chmod 1777 /tmp/.X11-unix && \
    chown root:root /tmp/.X11-unix

# This is read by the docker_entry.sh script,
# used to determine if tests or exmaples should be run
ENV FUSRR_RUN_TYPE=tests

# sets the virtual environment path for Hatch
ENV HATCH_ENV_TYPE_VIRTUAL_PATH=.venv

## -- Install packages --

# Install Python 3.10 (from a ppa), pip, and Hatch
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get install -y python3.10 python3-pip \
    # pyxdg seems to help the Docker container to run without errors
    && pip install --upgrade pip hatch pyxdg

# These deps are for PROCESS
RUN apt-get install -y \
    git \
    cmake \
    gfortran \
    lcov \
    poppler-utils

# -- Build and setup PROCESS --

RUN git clone --depth 1 --branch v3.1.0 https://github.com/ukaea/PROCESS
RUN cd PROCESS
RUN cmake -S . -B build && cmake --build build

# -- Copy in FusRR files --

WORKDIR /app

# These scripts run the tests and examples inside a Hatch virtual environment
COPY scripts ./scripts

# This script is the entrypoint for the Docker container
# which will run the scripts in the /scripts directory
# pyproject.toml and README.md are needed to run the Hatch virtual environments
COPY docker/docker_entry.sh pyproject.toml README.md ./

# The main source files
COPY examples ./examples
COPY tests ./tests
COPY fusrr ./fusrr

ENTRYPOINT [ "./docker_entry.sh" ]
