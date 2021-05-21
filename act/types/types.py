#!/usr/bin/env python3

""" Add ACT types """

import argparse
import functools
import json
import os
import re
import sys
from logging import critical, warning
from typing import Any, Dict, List, Text

from pkg_resources import resource_filename

import act.api

class TypeLoadError(Exception):
    pass


def parseargs() -> argparse.Namespace:
    """ Parse arguments """
    parser = argparse.ArgumentParser(description="ACT Bootstrap data model")
    parser.add_argument(
        "action",
        nargs=1,
        choices=['add', 'print'],
        help="Action (add or print)")
    parser.add_argument(
        "--default-object-types",
        action="store_true",
        help="Default object types")
    parser.add_argument(
        "--default-fact-types",
        action="store_true",
        help="Default fact types")
    parser.add_argument(
        "--default-meta-fact-types",
        action="store_true",
        help="Default meta fact types")
    parser.add_argument(
        "--object-types-file",
        help="Object type definitions (json)")
    parser.add_argument(
        "--fact-types-file",
        help="Fact type definitions (json)")
    parser.add_argument(
        "--meta-fact-types-file",
        help="Meta Fact type definitions (json)")
    parser.add_argument('--http-user', dest='http_user', help="ACT HTTP Basic Auth user")
    parser.add_argument(
        '--http-password',
        dest='http_password',
        help="ACT HTTP Basic Auth password")
    parser.add_argument("--logfile", help="Log to file (default = stdout)")
    parser.add_argument("--loglevel", default="info", help="Loglevel (default = info)")
    parser.add_argument("--userid", type=int, help="User ID")
    parser.add_argument(
        "--act-baseurl",
        dest="act_baseurl",
        help="API URI")

    return parser.parse_args()


def etc_file(filename: Text) -> Text:
    "Get content of file from resource/etc"
    return resource_filename("act.types", "etc/{}".format(filename))  # ).decode('utf-8')


def default_object_types():
    return load_types(etc_file("object-types.json"))


def default_fact_types():
    return load_types(etc_file("fact-types.json"))


def default_meta_fact_types():
    return load_types(etc_file("meta-fact-types.json"))


@functools.lru_cache(32)
def get_object_validator(object_type: Text) -> Text:
    """ Get object validator, default to act.api.DEFAULT_VALIDATOR) """

    typedef = [t for t in default_object_types() if t["name"] == object_type][0]

    if not typedef:
        raise TypeLoadError(f"Type not found: {object_type}")
    if len(typedef) > 1:
        raise TypeLoadError(f"Multiple types found for {object_type}")

    return typedef[0].get("validator", act.api.DEFAULT_VALIDATOR)


def object_validates(object_type: Text, object_value: Text) -> bool:
    """ Validate object using current valdiator """
    validator = get_object_validator(object_type)

    if re.search(validator, object_value):
        return True

    return False


def load_types(filename: Text) -> List[Dict]:
    """
    Parse as json, and exit on parse error
    """
    if not os.path.isfile(filename):
        raise TypeLoadError(f"File not found: {filename}")

    try:
        types = json.loads(open(filename, encoding="UTF8").read())
    except json.decoder.JSONDecodeError:
        raise TypeLoadError(f"Unable to parse file as json: {filename}")

    if not isinstance(types, list):
        raise TypeLoadError(f"Types must be a list of dicts")

    return types


def print_json(o: Any) -> None:
    " Print dict as sorted, indented json object "
    print(json.dumps(o, indent=4, sort_keys=True))


def create_object_types(client: act.api.Act, object_types: List[Dict]) -> None:
    """
    Create object types
    """

    existing_object_types = [object_type.name
                             for object_type in client.get_object_types()]

    # Create all objects
    for object_type in object_types:
        name = object_type["name"]
        validator = object_type.get("validator", act.api.DEFAULT_VALIDATOR)

        if name in existing_object_types:
            warning("Object type %s already exists" % name)
            continue

        client.object_type(name=name, validator_parameter=validator).add()


def create_fact_types(client: act.api.Act, fact_types: List[Dict]) -> None:
    """
    Create fact type with allowed bindings to ALL objects
    We want to change this later, but keep it like this to make it simpler
    when evaluating the data model
    """

    for fact_type in fact_types:
        name = fact_type["name"]
        validator = fact_type.get("validator", act.api.DEFAULT_VALIDATOR)
        object_bindings = fact_type.get("objectBindings", [])

        if not object_bindings:
            client.create_fact_type_all_bindings(
                name, validator_parameter=validator)

        else:
            client.create_fact_type(name, validator=validator, object_bindings=object_bindings)


def create_meta_fact_types(client: act.api.Act, meta_fact_types: List[Dict]) -> None:
    """
    Create fact type with allowed bindings to ALL objects
    We want to change this later, but keep it like this to make it simpler
    when evaluating the data model
    """

    for meta_fact_type in meta_fact_types:
        name = meta_fact_type["name"]
        validator = meta_fact_type.get("validator", act.api.DEFAULT_VALIDATOR)
        fact_bindings = meta_fact_type.get("factBindings", [])

        if not fact_bindings:
            client.create_meta_fact_type_all_bindings(name, validator_parameter=validator)

        else:
            client.create_meta_fact_type(name, fact_bindings=fact_bindings, validator=validator)


def main() -> None:
    "Main function"
    args = parseargs()

    if "print" in args.action:
        try:
            if args.default_object_types:
                print_json(default_object_types())

            if args.default_fact_types:
                print_json(default_fact_types())

            if args.default_meta_fact_types:
                print_json(default_meta_fact_types())

            if args.object_types_file:
                print_json(load_types(args.object_types_file))

            if args.fact_types_file:
                print_json(load_types(args.fact_types_file))

            if args.meta_fact_types_file:
                print_json(load_types(args.meta_fact_types_file))
        except TypeLoadError as e:
            critical(str(e))
            sys.exit(1)

        sys.exit(0)

    elif "add" in args.action:

        if not (args.act_baseurl and args.userid):
            sys.stderr.write("Missing --act-baseurl and/or --userid\n")
            sys.exit(1)

        auth = None
        if args.http_user:
            auth = (args.http_user, args.http_password)

        client = act.api.Act(
            args.act_baseurl,
            args.userid,
            args.loglevel,
            args.logfile,
            "act-types",
            requests_common_kwargs={'auth': auth})

        try:
            if args.default_object_types:
                create_object_types(client, default_object_types())

            if args.default_fact_types:
                create_fact_types(client, default_fact_types())

            if args.default_meta_fact_types:
                create_meta_fact_types(client, default_meta_fact_types())

            if args.object_types_file:
                create_object_types(client, load_types(args.object_types_file))

            if args.fact_types_file:
                create_fact_types(client, load_types(args.fact_types_file))

            if args.meta_fact_types_file:
                create_meta_fact_types(client, load_types(args.meta_fact_types_file))
        except TypeLoadError as e:
            critical(str(e))
            sys.exit(1)


if __name__ == "__main__":
    main()
