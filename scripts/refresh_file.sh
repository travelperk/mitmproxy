#!/usr/bin/env bash

# run this script to start the proxy, then from TDA run `python tests/performance/proxy_setup.py` to hit the proxy
# this script must be run from its virtual environment:
# mkvirtualenv mitmproxy ; pip install -r requirements.txt

mitmdump -s proxy.py

