#! /usr/bin/env python
# -*- encoding: utf-8 -*-
# Generate a lot of input files
#

import os

for routes in range(5,170+5,5):
    for bids in range(5,255+5,25):
        for test in range(4):
            cmd = 'python generator.py -r %d -b %d -o input/' % (routes, bids)
            print cmd
            os.system(cmd)
