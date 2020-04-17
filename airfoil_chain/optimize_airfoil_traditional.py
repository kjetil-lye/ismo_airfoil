#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 09:14:51 2020

@author: kjetil
"""

import numpy as np
import scipy.optimize
import json
import os.path
import optimizer_interface as opi
import ismo.objective_function
import sys
from ismo.submit import get_current_repository
from ismo.optimizers import make_bounds
import shutil
import pickle


class AirfoilComputer:
    def __init__(self, sample, path_to_main):
        self.sample = sample
        self.path_to_main = path_to_main
    
    def __call__(self, parameter):
        parameter_with_sample = np.zeros((1, parameter.shape[0]+1))
        parameter_with_sample[0,0] = self.sample
        parameter_with_sample[0,1:] = parameter
        
        opi.create_sample(self.sample, parameter_with_sample[0,:], self.path_to_main)
        opi.launch_solver(self.sample, self.path_to_main)
        
        sdata_file =f'SAMPLE_{self.sample}/sim_data.txt'
        
        data = np.loadtxt(sdata_file)
        
        shutil.rmtree(f'SAMPLE_{self.sample}', ignore_errors=True)
        return data

class WithObjective:
    def __init__(self, objective, computer):
        self.objective = objective
        self.computer = computer
        self.lift_drag_areas = []
        self.objective_values = []
        
        
    def __call__(self, parameter):
        lift_drag_area = self.computer(parameter)
        value = self.objective(lift_drag_area)
        
        self.lift_drag_areas.append(lift_drag_area)
        self.objective_values.append(value)
        return value
    

if __name__ == '__main__':
    print(f"Command line: {' '.join(sys.argv)}")
    import argparse
    from mpi4py import MPI
    from ismo.samples import create_sample_generator

    parser = argparse.ArgumentParser(description="""
Runs some complicated function on the input parameters
    """)

    parser.add_argument('--generator', type=str, default="monte-carlo",
                        help="Generator to use (either 'monte-carlo' or 'sobol'")

    parser.add_argument('--starting_sample', type=int, default=0,
                        help='The sample to start from')
    
    parser.add_argument('--number_of_samples', type=int, default=1,
                        help="Number of starting samples")
    
    parser.add_argument('--optimizer', type=str, default='L-BFGS-B',
                        help='Name of optimizer')
    
    parser.add_argument('--path_to_main', default=os.path.join(get_current_repository(), 'nuwtun_solver/examples/coupled_with_solver'),
                        help='Append output to end of file')
    args = parser.parse_args()

    
    generator = create_sample_generator(args.generator)

    dimension = 20
    parameters = generator(args.number_of_samples,
                        dimension,
                        start=args.starting_sample)
    
    
    
    
    optimize_target_file='objective.py'
    optimize_target_class='Objective'
    python_command='python'
    objective_parameter_file='penalties.json'
    
 
    with open(objective_parameter_file) as config_file:
        objective_configuration = json.load(config_file)
    
    objective_function = ismo.objective_function.load_objective_function_from_python_file(optimize_target_file,
                                                                                          optimize_target_class,
                                                                                          objective_configuration)

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    
    
    nproc = comm.Get_size()
    
    assert(nproc <= args.number_of_samples)
    
    samples_per_proc = (args.number_of_samples + nproc - 1) // nproc
    
    sample_index_start = rank * samples_per_proc
    sample_index_end = min(args.number_of_samples, (rank + 1)*samples_per_proc)
    
    
    
    all_optimization_results = []
    all_values = []
    all_lift_drag_areas = []
    
    if rank == 0:
        np.savetxt("traditional_optimization_parameters.txt", parameters)
    
    for sample_index in range(sample_index_start, sample_index_end):
        computer = AirfoilComputer(sample_index, args.path_to_main)
        
        with_objective = WithObjective(objective_function, computer)
        
        optimization_results = scipy.optimize.minimize(with_objective, 
                                                       parameters[sample_index-args.starting_sample],
                                                       bounds=make_bounds([0,1], parameters[sample_index-args.starting_sample]))
        all_optimization_results.append(optimization_results)
        
        all_values.append(with_objective.objective_values)
        all_lift_drag_areas.append(with_objective.lift_drag_areas)
        print(optimization_results)
    comm.barrier()
    
    output_to_save = {
            "all_optimization_results" : all_optimization_results,
            "all_values" : all_values,
            "all_lift_drag_areas" : all_lift_drag_areas}
    
    for name, array in output_to_save.items():
        full_array = comm.gather(array, root=0)
        if rank == 0:
            with open(f'traditional_optimization_{name}.pic', 'wb') as outputfile:
                pickle.dump(full_array, outputfile)
        
        
    