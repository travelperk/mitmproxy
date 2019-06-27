#!/usr/bin/env python
#
# Simple script showing how to read a mitmproxy dump file
#
from mitmproxy import io
from mitmproxy.exceptions import FlowReadException
import pprint
import sys


with open(sys.argv[1], "rb") as logfile:
    freader = io.FlowReader(logfile)
    pp = pprint.PrettyPrinter(indent=4)
    try:
        for f in freader.stream():
            if f.request:
                print(f"{f.request.method} {f.request.url}")
            # pp.pprint(f.get_state())
            print("")
    except FlowReadException as e:
        print("Flow file corrupted: {}".format(e))
