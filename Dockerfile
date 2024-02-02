FROM lscr.io/linuxserver/blender:latest

# RUN python pip install hatch

# COPY pyproject.toml /

# RUN hatch shell


RUN mkdir /code

WORKDIR /code

COPY examples/simple_scene.ex.py /code/simple_scene.ex.py

COPY examples/ fussr/ pyproject.toml ./


CMD ["blender", "--background", "--python", "simple_scene.ex.py"]
# CMD ["blender", "--background"]
# CMD ["blender", "--background", "--python-expr", "import bpy; bpy.ops.wm.source(filepath='code/simple_scene.ex.py')"]

