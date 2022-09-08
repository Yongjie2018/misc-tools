#!/usr/bin/env python3

# converting file from below two lines to a single line format
# from:
# started Tue Sep  6 05:05:57 UTC 2022
# stopped Tue Sep  6 05:07:38 UTC 2022
# to:
# 2022-09-06 05:05:57+00:00 , 0:01:41

import sys
from dateutil.parser import parse

with open(sys.argv[1]) as myfile:
    for line in myfile:
        if (line[0:8] == "started "):
            dt1 = parse(line[8:-1])
        elif (line[0:8] == "stopped "):
            dt2 = parse(line[8:-1])

print(dt1, ',', dt2 - dt1)
