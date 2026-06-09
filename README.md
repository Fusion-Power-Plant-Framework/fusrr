# **FusRR**

**Fus**ion **R**eactor **R**enderer

<img width="500" height="500" alt="Image" src="https://github.com/user-attachments/assets/28a17dfb-0e67-49c4-b2c0-5fcd8a776458" />

## Developing visualisations of fusion reactors

The aim of this repository is to take outputs from ``PROCESS`` and `BLUEMIRA` and render them to be able to produce useful visualisations in Blender.

> [! NOTE]
> We are tied to the Python version required by the Blender module, bpy.
> Currently this is Python 3.13 - 3.13.8.

## Setup

This project required [Git LFS](https://github.com/git-lfs/git-lfs). Git LFS is commonly part of Git and installed along with it, but you can install it on Ubuntu:

```bash
sudo apt install git-lfs
```

To get bpy module types, install the following dependencies:

```bash
pip install fake-bpy-module
```

This project uses [Hatch](https://hatch.pypa.io/latest/). Although any Python environment manager can be used, we recommend using the default environment setup by Hatch.


### With Hatch

To start using Hatch, it must be installed and accessible from the command line. See the Hatch [installation](https://hatch.pypa.io/latest/install/) for more.

A simple way to install Hatch is to run:

```bash
pip install hatch
```

If you can run `hatch -h` then Hatch has been successfully installed.


We recommend setting the `dirs.env` in your hatch config to the following:

```toml
[dirs.env]
virtual = ".hatch"
```

The path to this file can be found by running:

```bash
hatch config find
```

It makes it easier to set the path to environment in your code editor.

Then run:

```bash
hatch shell
```

This will create the default hatch environment in the project folder.

If using an editor, set the path to your Python environment in your editor to `.hatch/fusrr/bin/python`.

### Without Hatch

Setup and activate your environment with your chosen Python environment manager (pyenv, conda, virtualenv, etc.)

> [!IMPORTANT]
> Ensure your Python version is between 3.13 - 3.13.8.

Run the following to install this project as a local editable install, with the necessary optional dependency groups:

```bash
python -m pip install -e .'[dev,test,lint]'
```

## Installing PROCESS

After your environment has been setup, you will need to install PROCESS.

Make sure your environment is active, then run the following:

```bash
pip install -e .'[process]'
```

## Tests

If using Hatch, run:

```bash
hatch run test:tests
```

Else use pytest:

```bash
pytest tests
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

If you are experiencing issues with Python versions setting to a default rather than the necessary 3.13 - 3.13.8 required for `fusrr`, run this before running `hatch shell` again:

```bash
hatch env remove default
```


## Licence Information

**FusRR** is [released under the MIT License](LICENCE)
