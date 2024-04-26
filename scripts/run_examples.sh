#!/bin/bash

hatch shell

cd examples

echo "Running simple_scene.py"
python simple_scene.py

cd eudemo

echo "Running eudemo.py"
python eudemo.py

exit 0