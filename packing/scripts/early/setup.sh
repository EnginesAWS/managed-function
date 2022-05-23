#!/bin/sh
/usr/local/bin/python -m pip install --upgrade pip
pip install -q awscliv2 --upgrade
pip install -r /tmp/python_packages.txt
