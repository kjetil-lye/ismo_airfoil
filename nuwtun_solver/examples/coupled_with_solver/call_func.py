#!/usr/bin/env python
# Python wrapper for interfacing between optimizer and nuwtun
# Author: Deep Ray, EPFL
# Date  : 19 April, 2019

import optimizer_interface as opi
import os
import numpy as np

rnd_file = '../../rnd_nbs/sobol_nbs_20.txt'
assert(os.path.exists(rnd_file))
path_to_main = '.'
params = np.loadtxt(rnd_file)

sid = 1
for i in range(4):
    values = opi.run_simulator(sid, params[(sid-1):(sid+2),::],path_to_main)
    print(values)
    sid = sid + 3
