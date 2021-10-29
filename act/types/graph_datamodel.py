#!/usr/bin/env python3

import argparse
import datetime
import os
import pickle
import urllib.parse
from typing import Generator, Optional, Tuple

import graphviz
import requests

from atlassian import Confluence


class DataModel:

    DEBUG = False

    def __init__(
        self,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        user_id: int = 0,
        cacert: str = "",
    ) -> None:
        self.objects_url = urllib.parse.urljoin(url, "/v1/objectType")
        self.facts_url = urllib.parse.urljoin(url, "/v1/factType")
        self.username = username
        self.password = password
        self.user_id = user_id
        self.status: Optional[int] = None
        self._objects: Optional[dict] = None
        self._facts: Optional[dict] = None
        self.verify = cacert if cacert != "" else True

    def load(self) -> None:
        """Download the datamodel from the act instance"""

        headers = {"ACT-User-ID": str(self.user_id), "Accept": "application/json"}
        auth = (self.username, self.password)

        if self.username:
            r = requests.get(
                self.objects_url, auth=auth, headers=headers, verify=self.verify
            )
        else:
            r = requests.get(self.objects_url, headers=headers, verify=self.verify)

        if r.status_code == 200:
            self._objects = r.json()
        else:
            if self.DEBUG:
                print("Error loading objects: {}".format(r.status_code))
            self._objects = None
            self._facts = None
            self.status = r.status_code
            return

        if self.username:
            r = requests.get(
                self.facts_url, auth=auth, headers=headers, verify=self.verify
            )
        else:
            r = requests.get(self.facts_url, headers=headers, verify=self.verify)

        if r.status_code == 200:
            self._facts = r.json()
        else:
            if self.DEBUG:
                print("Error loading objects: {}".format(r.status_code))
            self._objects = None
            self._facts = None
            self.status = r.status_code
            return

        self.status = r.status_code

    def __eq__(self, other: object) -> bool:
        return set(self.objects) == set(other.objects) and set(self.facts) == set(
            other.facts
        )

    @property
    def facts(self) -> Generator[Tuple[str, str, str, bool], None, None]:
        """Iterate over fact bindings"""

        if not self._facts:
            if self.DEBUG:
                print("Trying to iterate over None facts")
            return
        for fact in self._facts["data"]:
            if not fact:
                print("Nonetype", fact)
                continue
            bindings = fact["relevantObjectBindings"]
            if not bindings:
                continue
            for binding in bindings:
                yield (
                    fact["name"],
                    binding["sourceObjectType"]["name"],
                    binding["destinationObjectType"]["name"]
                    if binding["destinationObjectType"]
                    else None,
                    binding["bidirectionalBinding"],
                )

    @property
    def objects(self) -> Generator[str, None, None]:
        """Iterate over object bindings"""

        if not self._objects:
            if self.DEBUG:
                print("Trying to iterate over None objects")
            return

        for obj in self._objects["data"]:
            if not obj:
                print("Nonetype", obj)
                continue
            yield obj["name"]


def parse_args() -> argparse.Namespace:
    """Handle command line arguments, returning the arguments ns"""

    parser = argparse.ArgumentParser(description="Build a graph of the act datamodel")
    parser.add_argument("url", type=str, help="Url of the act instance to graph")
    parser.add_argument("--uid", default=1, type=int, help="Act user ID")
    parser.add_argument("--http_username", type=str, default=None, help="HTTP Username")
    parser.add_argument("--http_password", type=str, default=None, help="HTTP Password")
    parser.add_argument("--parent_id", type=int, default=None, help="Confluence upload")
    parser.add_argument(
        "--confluence_url", type=str, default=None, help="Confluence api url"
    )
    parser.add_argument(
        "--confluence_user", type=str, default=None, help="Confluence user"
    )
    parser.add_argument(
        "--confluence_password", type=str, default=None, help="Confluence password"
    )
    parser.add_argument(
        "--dump_source",
        type=str,
        default=None,
        help="Dump graphviz source to directory",
    )
    parser.add_argument(
        "--cacert",
        type=str,
        default=None,
        help="If you need to specify a CA certificate file",
    )

    return parser.parse_args()


def run() -> None:
    """Main program loop"""

    args = parse_args()

    dm = DataModel(
        args.url, args.http_username, args.http_password, args.uid, args.cacert
    )
    dm.load()

    if dm.status != 200:
        print("{} Status code {}".format(str(datetime.datetime.now()), dm.status))
        return

    try:
        old_dm = pickle.load(open("cache.dat", "rb"))
        if old_dm == dm:
            return
    except FileNotFoundError:
        print("First run")

    print("{} Graphing changes".format(str(datetime.datetime.now())))

    pickle.dump(dm, open("cache.dat", "wb"))

    dot = graphviz.Digraph(comment="Double edge facts")

    # for obj in dm.objects:
    #     dot.node(obj, obj)

    for fact in dm.facts:
        name, s, d, di = fact
        if name == "mentions":
            continue
        if not d:
            continue

        dot.node(s, s)
        dot.node(d, d)
        if di:
            dot.edge(s, d, label=name, dir="both")
        else:
            dot.edge(s, d, label=name)

    if args.dump_source:
        with open(os.path.join(args.dump_source, "double.dot"), "w") as f:
            f.write(dot.source)

    dot.render("output/double", format="png", renderer="cairo")

    dot = graphviz.Digraph(comment="Single edge facts")

    for fact in dm.facts:

        name, s, d, di = fact

        if d:
            continue

        dot.node(name, label=name, shape="diamond")
        dot.node(s, s)

        dot.edge(s, name)

    if args.dump_source:
        with open(os.path.join(args.dump_source, "single.dot"), "w") as f:
            f.write(dot.source)

    dot.render("output/single", format="png", renderer="cairo")

    dot = graphviz.Digraph(comment="All Double edge facts")

    for obj in dm.objects:
        dot.node(obj, obj)

    for fact in dm.facts:
        name, s, d, di = fact
        if not d:
            continue

        dot.node(s, s)
        dot.node(d, d)
        if di:
            dot.edge(s, d, label=name, dir="both")
        else:
            dot.edge(s, d, label=name)

    if args.dump_source:
        with open(os.path.join(args.dump_source, "complete.dot"), "w") as f:
            f.write(dot.source)

    dot.render("output/complete", format="png", renderer="cairo")

    if args.parent_id:
        try:
            os.environ.pop("https_proxy")
        except KeyError:
            pass
        try:
            os.environ.pop("http_proxy")
        except KeyError:
            pass

        verify_ssl = False if args.cacert else True

        confluence = Confluence(
            url=args.confluence_url,
            username=args.confluence_user,
            password=args.confluence_password,
            verify_ssl=verify_ssl,
        )
        confluence.attach_file(
            "output/double.cairo.png",
            page_id=args.parent_id,
            title="Double Edged Facts",
        )
        confluence.attach_file(
            "output/single.cairo.png",
            page_id=args.parent_id,
            title="Single Edged Facts",
        )
        confluence.attach_file(
            "output/complete.cairo.png",
            page_id=args.parent_id,
            title="Single Edged Facts",
        )

        if args.dump_source:
            confluence.attach_file(
                os.path.join(args.dump_source, "complete.dot"),
                page_id=args.parent_id,
                title="complete source",
            )
            confluence.attach_file(
                os.path.join(args.dump_source, "double.dot"),
                page_id=args.parent_id,
                title="double source",
            )
            confluence.attach_file(
                os.path.join(args.dump_source, "single.dot"),
                page_id=args.parent_id,
                title="single source",
            )


if __name__ == "__main__":
    run()
