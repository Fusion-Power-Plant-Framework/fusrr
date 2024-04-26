FROM lscr.io/linuxserver/blender:latest

# Create the /tmp/.X11-unix directory with the appropriate permissions
RUN mkdir /tmp/.X11-unix && \
chmod 1777 /tmp/.X11-unix && \
chown root:root /tmp/.X11-unix

WORKDIR /app

# Install Python 3.10
RUN apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y python3.10 python3-pip \
    && pip install --upgrade pip

RUN pip install pyxdg

ENV HATCH_ENV_TYPE_VIRTUAL_PATH=.venv
RUN pip install hatch

COPY pyproject.toml README.md ./
RUN mkdir ./fusrr && touch fusrr/_version.py
RUN hatch shell

COPY scripts ./scripts

COPY examples ./examples
COPY tests ./tests
COPY fusrr ./fusrr

CMD ["bash", "scripts/run_tests.sh"]

# CMD ["blender", "--background", "--python", "examples/simple_scene.py"]
# CMD ["blender", "--background"]
# CMD ["blender", "--background", "--python-expr", "import bpy; bpy.ops.wm.source(filepath='code/simple_scene.ex.py')"]
