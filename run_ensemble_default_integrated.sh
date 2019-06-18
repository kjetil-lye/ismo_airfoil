#!/bin/bash

source source_nuwtun.sh
export PYTHONPATH=${PYTHONPATH}:$(pwd)/iterative_surrogate_optimization
mkdir ensemble_output
cd ensemble_output
python ../ensemble_run/run_ensemble_integrated.py "$@"
