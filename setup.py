#!/usr/bin/env python

from setuptools import setup

setup(
    name="tap-db2",
    version="1.0.1",
    description="Tap for extracting data from an IBM DB2 database",
    author="Mark Johnston, Tom Sloman",
    url="TO-DO",
    classifiers=[
        # "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    py_modules=["tap_db2"],
    install_requires=[
        "attrs==22.2.0",
        "ibm-db-sa==0.3.8",
        "ibm-db==3.1.4",
        "jinja2==3.1.2",
        "markupsafe<2.2.0",
        "pendulum==2.1.2",
        "pyodbc==4.0.35",
        "pytz>=2018.1",
        "singer-python>=5.12.0",
        "sqlalchemy<3.0.0",
    ],
    entry_points="""
          [console_scripts]
          tap-db2=tap_db2:main
      """,
    packages=["tap_db2", "tap_db2.sync_strategies"],
)
