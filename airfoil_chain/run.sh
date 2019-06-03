#!/bin/bash
set -e
bash ../run_python_script.sh submit_airfoil.py --number_of_samples_per_iteration 2 2 2 2 "$@"
