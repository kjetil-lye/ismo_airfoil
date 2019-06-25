#!/bin/bash

source source_for_nuwtun.sh
export PYTHONPATH=${PYTHONPATH}:$(pwd)/iterative_surrogate_optimization:$(pwd)
mkdir ensemble_output_sobol
cd ensemble_output_sobol
python ../ensemble_run/run_ensemble_integrated.py "$@"
