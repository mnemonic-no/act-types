"""Setup script for the python-act library module"""

from os import path

from setuptools import setup

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), "rb") as f:
    long_description = f.read().decode("utf-8")

setup(
    name="act-types",
    version="2.1.1",
    author="mnemonic AS",
    zip_safe=True,
    author_email="opensource@mnemonic.no",
    description="ACT type handling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="ACT, mnemonic",
    entry_points={
        "console_scripts": [
            "act-graph-datamodel = act.types.graph_datamodel:run",
        ]
    },
    # Include ini-file(s) from act/workers/etc
    package_data={"act.types": ["etc/*.json"]},
    packages=["act.types"],
    # https://packaging.python.org/guides/packaging-namespace-packages/#pkgutil-style-namespace-packages
    # __init__.py under all packages under in the act namespace must contain exactly string:
    # __path__ = __import__('pkgutil').extend_path(__path__, __name__)
    namespace_packages=["act"],
    url="https://github.com/mnemonic-no/act-workers",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, <4",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "License :: OSI Approved :: ISC License (ISCL)",
    ],
)
