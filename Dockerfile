FROM linuxserver/blender:latest

# Create the /tmp/.X11-unix directory with the appropriate permissions
RUN mkdir /tmp/.X11-unix && \
chmod 1777 /tmp/.X11-unix && \
chown root:root /tmp/.X11-unix

ENV HATCH_ENV_TYPE_VIRTUAL_PATH=.venv

WORKDIR /app

# Install Python 3.10
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.10 python3-pip \
    && pip install --upgrade pip hatch

RUN pip install pyxdg

COPY pyproject.toml README.md ./

# Due to the way hatch runs
# we cannot create the environment prior
# RUN mkdir ./fusrr && touch fusrr/_version.py
# RUN hatch shell

COPY scripts ./scripts

COPY examples ./examples
COPY tests ./tests
COPY fusrr ./fusrr

CMD ["bash", "scripts/run_tests.sh"]
