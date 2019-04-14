#!/usr/bin/env python3

""" Add ACT types """

import argparse
import json
import sys
from logging import critical, warning
from typing import Dict, Text

from pkg_resources import resource_string

import act.api


def parseargs() -> argparse.Namespace:
    """ Parse arguments """
    parser = argparse.ArgumentParser(description="ACT Bootstrap data model")
    parser.add_argument(
        "--add-default-object-types",
        action="store_true",
        help="Add default object types")
    parser.add_argument(
        "--add-default-fact-types",
        action="store_true",
        help="Add default fact types")
    parser.add_argument(
        "--add-default-meta-fact-types",
        action="store_true",
        help="Add default meta fact types")
    parser.add_argument(
        "--print-default-object-types",
        action="store_true",
        help="Print default object types and exit")
    parser.add_argument(
        "--print-default-fact-types",
        action="store_true",
        help="Print default fact types and exit")
    parser.add_argument(
        "--print-default-meta-fact-types",
        action="store_true",
        help="Print default meta fact types and exit")
    parser.add_argument(
        "--object-types-file",
        type=argparse.FileType('r', encoding='UTF-8'),
        help="Object type defintions (json)")
    parser.add_argument(
        "--fact-types-file",
        type=argparse.FileType('r', encoding='UTF-8'),
        help="Fact type defintions (json)")
    parser.add_argument(
        "--meta-fact-types-file",
        type=argparse.FileType('r', encoding='UTF-8'),
        help="Meta Fact type defintions (json)")
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
    return resource_string("act.types", "etc/{}".format(filename)).decode('utf-8')


def etc_json(filename: Text) -> Dict:
    "Get content of file from resource/etc"
    return parse_json(etc_file(filename))


def parse_json(json_str: Text) -> Dict:
    """
    Parse as json, and exit on parse error
    """
    try:
        return json.loads(json_str)
    except json.decoder.JSONDecodeError:
        critical("Unable to parse file as json: %s" % json_str)
        sys.exit(1)


def create_object_types(client: act.api.Act, object_types: Dict) -> None:
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


def create_fact_types(client: act.api.Act, fact_types: Dict) -> None:
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


def create_meta_fact_types(client: act.api.Act, meta_fact_types: Dict) -> None:
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

    if args.print_default_object_types:
        print(etc_file("object-types.json"))
        sys.exit(0)

    if args.print_default_fact_types:
        print(etc_file("fact-types.json"))
        sys.exit(0)

    if args.print_default_meta_fact_types:
        print(etc_file("meta-fact-types.json"))
        sys.exit(0)

    if not args.act_baseurl and args.userid:
        sys.stderr.write("Missing --act-baseurl and/or --userid\n")
        sys.exit(1)

    client = act.api.Act(
        args.act_baseurl,
        args.userid,
        args.loglevel,
        args.logfile,
        "act-types")

    if args.add_default_object_types:
        create_object_types(client, etc_json("object-types.json"))

    if args.add_default_fact_types:
        create_fact_types(client, etc_json("fact-types.json"))

    if args.add_default_meta_fact_types:
        create_meta_fact_types(client, etc_json("meta-fact-types.json"))

    if args.object_types_file:
        create_object_types(client, args.object_types_file.read())

    if args.fact_types_file:
        create_fact_types(client, args.fact_types_file.read())

    if args.meta_fact_types_file:
        create_meta_fact_types(client, args.meta_fact_types_file.read())


if __name__ == "__main__":
    main()
