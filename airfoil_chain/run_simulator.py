from optimize_airfoil_traditional import AirfoilComputer

import sys
import numpy as np
import objective
import json


filename = sys.argv[1]
line = int(sys.argv[2])

parameters = np.loadtxt(filename)

path_to_main='../nuwtun_solver/examples/coupled_with_solver'
sample = 0
computer = AirfoilComputer(sample, path_to_main)


with open('penalties.json') as f:
    penalties = json.load(f)
objective_function = objective.Objective(**penalties)
lift_drag_area = computer(parameters[line,:])
objective_value = objective_function(lift_drag_area)
print(f'    {line:3d}: ' + (' '.join(f'{x:.8e}' for x in lift_drag_area)) + f"    ({objective_value:.8e})")
