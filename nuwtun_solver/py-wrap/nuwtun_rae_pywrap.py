#!/usr/bin/env python
# Python wrapper for nuwtun
# Author: Deep Ray, EPFL
# Date  : 19 April, 2019

import numpy as np
from sys import argv, exit
import re
import os, errno
import subprocess

def clean(string):
    sa, sb = '', ''
    a = string.split(' ')
    for s in a:
        sa = sa + s
    if "\t" in sa:
        sb = sa.strip("\t")
        for s in sb:
            sa = sa + s
    return sa

def extract_info(s):
    if len(s)==2:
        key = s[0]
        value = s[1]
        return str(clean(key)), str(value)
    else:
        return "error", "error"

def rs(string):
    ns = ''
    for i in string:
        if i not in [' ']:
            ns = ns + i
    return ns


def read_parameter(input):
    in_file = open(input, 'r')
    d = {}
    for line in in_file:
        s =  line[:-1].split("=")
        key, value = extract_info(s)
        if key != "error":
            d[key] = value
    in_file.close()
    return d

def mesh_pert(d):
    print ("\n\n    --- READING AND DEFORMING MESH\n\n")
    # Check if necessary input files are available
    assert(os.path.exists('grid.0'))
    assert(os.path.exists('shape.in'))
    assert(os.path.exists('shape.dat'))

    comline = "deform > output_deform.out"
    #subprocess.run("deform")
    os.system(comline)

def find_area(d):
    print ("    --- FINDING AREA ENCLOSED BY AIRFOIL\n")
    # Check if necessary input files are available
    assert(os.path.exists('grid.unf'))
    assert(os.path.exists('shape.in'))
    assert(os.path.exists('area.in'))

    comline = "area  > output_area.out"
    os.system(comline)
    #subprocess.run("area")

def init_solver(d):
    print ("    --- STARTING SOLVER\n")
    pname = rs(d['solver_input_file'])
    # Check if necessary input files are available
    assert(os.path.exists('grid.unf'))
    assert(os.path.exists(pname))

    comline = "nuwtun_flo < "+pname+" > output_solver.out"
    os.system(comline)

def extract_data(d):
    print ("    --- EXTRACTING DATA\n\n")

    # Check if necessary input files are available
    if(os.path.exists('fort.19')):   # File is absent id simulation failed
        assert(os.path.exists('area.out'))
        area     = np.loadtxt('area.out')
        with open('fort.19', 'r') as file:
            line = file.readline()
            while line:
                line_data = [x.strip() for x in line.split(' ')]
                data = [val for val in line_data if val != '' and val !='\n']
                if(data[0] == 'CL'):
                    cl_val = float(data[1])
                if(data[0] == 'CD'):
                    cd_val = float(data[1])
                line = file.readline()

        file.close()

        out_data = np.array([cl_val,cd_val,area])
        np.savetxt('sim_data.txt',out_data.reshape(1, out_data.shape[0]),fmt='%.10e')


# wrapper begins here:
script, input = argv
param_map = read_parameter(input)

print ("    ---------------------------------------------------------------------------\n")
print ("    INITIATING REQUESTED TASKS: \n")

# execution of main operations
if rs(param_map['mesh_pert']) == 'yes':
    mesh_pert(param_map)
if rs(param_map['find_area']) == 'yes':
    find_area(param_map)
if rs(param_map['initiate_solver']) == 'yes':
    init_solver(param_map)
if rs(param_map['extract_data']) == 'yes':
    extract_data(param_map)
print ("    ---------------------------------------------------------------------------\n")
