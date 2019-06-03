#!/bin/bash
set -e
source source_for_nuwtun.sh
cd nuwtun_solver
cd src-flo
make
cd ..
cd src-grd
make deform area
