# **renderingpipeline**

![image](examples/initial_collage.png)


## Developing visualisations of fusion reactors.
The aim of this repository is to take outputs from ``PROCESS`` and `BLUEMIRA` and render them to be able to produce useful visualisations in Blender.

## Work in Progress!
The rendering pipeline is still in the early stages of development and therefore can only produce certain reactor designs from `PROCESS` and import CAD output from `BLUEMIRA`

## Installation

With a python environment active you will need to first install `PROCESS`. Then, once you have cloned the repository, change into the directory and run `pip install -e./` to install **renderingpipeline** in your python environment.

If you want to run the tests you will also need to install the develop dependencies:

```
bash

> pip install -e "./[dev]"
> pytest

```




## Usage
Renderingpipeline is intended to be used with a `PROCESS` MFILE and/or a `bluemira` CAD output file. Both files can be read by the `Reactor` object and then used to create a view of the reactor.

An example of how to create a reactor from an MFILE is shown in `examples/example_view.ipynb`.



## Licence Information
**renderingpipeline** is [released under the MIT License](LICENCE)
