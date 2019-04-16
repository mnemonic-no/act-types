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
