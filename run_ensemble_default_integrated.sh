#!/bin/bash

source source_for_nuwtun.sh
export PYTHONPATH=${PYTHONPATH}:$(pwd)/iterative_surrogate_optimization:$(pwd)
mkdir ensemble_output
cd ensemble_output
python ../ensemble_run/run_ensemble_integrated.py "$@"
