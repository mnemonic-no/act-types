# ACT types

## Introduction

These scripts are used to add types to the [ACT](https://github.com/mnemonic-no/act-platform) data model (object types and fact types).

## Installation
1. This project requires that you have a running installation of the [act-platform](https://github.com/mnemonic-no/act-platform).
2. Install from pip
```bash
pip install act-types
```

## Breaking changes

### 2.0 Updated data model

This version includes breaking changes to the data model. It is advised to do a reimport of all data and import using act-worker with version >= 2.0.0.

The following changes are implemented:
- act-types and act-graph-datamodel is moved to act-admin and act-utils.

# Local development

Use pip to install in [local development mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs). act-types (and act-api) uses namespacing, so it is not compatible with using `setup.py install` or `setup.py develop`.

In repository, run:

```bash
pip3 install --user -e .
```

It is also necessary to install in local development mode to correctly resolve the files that are read by the `--default-*` options when doing local changes. These are read from etc under act.types and if the package is installed with "pip install act-types" it will always read the files from the installed package, even though you do changes in a local checked out repository.
