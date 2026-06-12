# **FusRR**

**Fus**ion **R**eactor **R**enderer

<img width="500" height="500" alt="Image" src="https://github.com/user-attachments/assets/28a17dfb-0e67-49c4-b2c0-5fcd8a776458" />

## Developing visualisations of fusion reactors

The aim of this repository is to take outputs from [`PROCESS`](https://github.com/ukaea/PROCESS) and [`Bluemira`](https://github.com/Fusion-Power-Plant-Framework/bluemira) and render them to be able to produce useful visualisations in Blender.

> [!NOTE]
> We are tied to the Python version required by the Blender module, bpy.
> Currently this is Python 3.13.

## Setup

This project uses [Hatch](https://hatch.pypa.io/latest/). Although any Python environment manager can be used, we recommend using the default environment setup by Hatch.

### With Hatch

To start using Hatch, it must be installed and accessible from the command line. See the Hatch [installation](https://hatch.pypa.io/latest/install/) for more.

A simple way to install Hatch is to run:

```bash
pip install hatch
```

If you can run `hatch -h` then Hatch has been successfully installed.


Then run:

```bash
hatch shell
```

This will create the default hatch environment in the project folder.

### Without Hatch

Setup and activate your environment with your chosen Python environment manager (pyenv, conda, virtualenv, etc.)

```bash
python -m pip install .
```

## Installing PROCESS

After your environment has been setup, you will need to install PROCESS.

Make sure your environment is active, then run the following:

```bash
python -m pip install -e .'[process]'
```

## Troubleshooting

### Hatch

> [!IMPORTANT]
> Ensure you have Hatch version 1.13.0 or later, otherwise it won't cover Python 3.13.

If you already have Hatch installed, check your version by running:

```bash
hatch --version
```

If it is below 1.13.0, please update it:

```bash
pip install --upgrade hatch
```

If you are experiencing issues with Python versions setting to a default rather than the necessary 3.13.0 - 3.13.8 required for `fusrr`, run this before running `hatch shell` again:

```bash
hatch env remove default
```

## Development

Run the following to install this project as a local editable install, with the necessary optional dependency groups:

```bash
python -m pip install -e .'[dev, test, lint]'
```

Install the following dependencies to enable code completion of Blender Python API modules in commonly used IDEs:

```bash
pip install fake-bpy-module
```

If using Hatch: to make it easier to set the path to environment in your code editor, we recommend setting the `dirs.env` in your hatch config to the following:

```toml
[dirs.env]
virtual = ".hatch"
```

The path to this file can be found by running:

```bash
hatch config find
```

If using an editor, set the path to your Python environment in your editor to `.hatch/fusrr/bin/python`.

## Licence Information

**FusRR** is [released under the MIT License](LICENCE)
