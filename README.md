# ACT types

## Introduction

These scripts are used to add types to the [ACT](https://github.com/mnemonic-no/act-platform) data model (object types and fact types).

## Installation
1. This project requires that you have a running installation of the [act-platform](https://github.com/mnemonic-no/act-platform).
2. Install from pip
```bash
pip install act-types
```

## act-types usage
To bootstrap the type system with default types (userid/act-baseurl must point to ACT installation):
```
act-types \
    --userid 1 \
    --act-baseurl http://localhost:8888 \
    --loglevel ERROR \
    --default-object-types \
    --default-fact-types \
    --default-meta-fact-types \
    add
```

It is safe to rerun the command above, after new types have been added to the data model.

You can also add types from your own files, using --object-types-file, --fact-types-file and --meta-fact-types-file that points to a json file on the same format as the [default types](https://github.com/mnemonic-no/act-types/tree/master/act/types/etc).

To print default types (replace with fact/meta-fact for other types):
```bash
act-types --default-object-types print
```

## act-graph-datamodel usage

Build a graph (graphviz) of the ACT data model.
```bash
act-graph-datamodel --help
usage: act-graph-datamodel [-h] [--uid UID] [--http_username HTTP_USERNAME]
                           [--http_password HTTP_PASSWORD]
                           [--parent_id PARENT_ID]
                           [--confluence_url CONFLUENCE_URL]
                           [--confluence_user CONFLUENCE_USER]
                           [--confluence_password CONFLUENCE_PASSWORD]
                           url
```

# Local development

Use pip to install in [local development mode](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs). act-types (and act-api) uses namespacing, so it is not compatible with using `setup.py install` or `setup.py develop`.

In repository, run:

```bash
pip3 install --user -e .
```

It is also necessary to install in local development mode to correctly resolve the files that are read by the `--default-*` options when doing local changes. These are read from etc under act.types and if the package is installed with "pip install act-types" it will always read the files from the installed package, even though you do changes in a local checked out repository.
