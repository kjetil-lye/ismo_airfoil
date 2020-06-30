import json
import sys
import objective
lift = float(sys.argv[1])
drag = float(sys.argv[2])
area = float(sys.argv[3])

with open('penalties.json') as f:
    penalties = json.load(f)

objective_function = objective.Objective(**penalties)
print(objective_function([lift, drag, area]))
