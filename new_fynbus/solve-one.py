#! /usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Solve a single input file
#

import os
import sys
import random

fns = os.listdir('input')
random.shuffle(fns)

for fn in fns:
    if not fn.endswith('txt'):
        continue
    # move to current
    lfn = os.path.join('input', fn)
    cfn = os.path.join('current', fn)
    try:
        os.rename(lfn, cfn)
        break
    except OSError:
        continue
else:
    print 'No files left'
    sys.exit(0)
    
cmd = 'python fynbus_to_kombee.py -i %s > %s.stdout' % (cfn, cfn)
os.system(cmd)
    
cmd = 'python solution.py -i %s > %s.modified.stdout' % (cfn, cfn)
os.system(cmd)


# move to done
for f in os.listdir('current'):
    if not f.startswith(fn):
        continue
    os.rename(os.path.join('current', f), os.path.join('done', f))
        

