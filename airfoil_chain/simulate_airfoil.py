import numpy as np
import os.path
from ismo.submit import get_current_repository

if __name__ == '__main__':
    import argparse
    from mpi4py import MPI
    import optimizer_interface as opi

    parser = argparse.ArgumentParser(description="""
Runs some complicated function on the input parameters
    """)

    parser.add_argument('--input_parameters_file', type=str, required=True,
                        help='Input filename for the parameters (readable by np.loadtxt)')

    parser.add_argument('--output_values_files', type=str, required=True, nargs="+",
                        help='Output filename for the values (will be written by np.savetxt)')

    parser.add_argument('--starting_sample', type=int, required=True,
                        help='The starting id of the first sample')

    parser.add_argument('--iteration_number', type=int, required=True,
                        help='The iteration number')
    
    
    parser.add_argument('--start', type=int, default=0,
                        help='Starting index to read out of the parameter file, by default reads from start of file')

    parser.add_argument('--end', type=int, default=-1,
                        help='Ending index (exclusive) to read out of the parameter file, by default reads to end of file')

    parser.add_argument('--output_append', action='store_true',
                        help='Append output to end of file')
    
    parser.add_argument('--path_to_main_dir', default=os.path.join(get_current_repository(), 'nuwtun_solver/examples/coupled_with_solver'),
                        help='Append output to end of file')

    

    args = parser.parse_args()
    
    path_to_main_dir = args.path_to_main_dir
    starting_sample_id = args.starting_sample
    iteration_number = args.iteration_number

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if args.end != -1:
        parameters = np.loadtxt(args.input_parameters_file)[args.start:args.end]
    else:
        parameters = np.loadtxt(args.input_parameters_file)[args.start:]
        
    # rearranging so that it is compatible with the simulator
    parameters_new = np.zeros((parameters.shape[0], parameters.shape[1]+1))

    for n in range(parameters.shape[0]):
        parameters_new[n, 1:] = parameters[n, :]
        parameters_new[n, 0] = n + args.starting_sample
    
    parameters = parameters_new

    values = opi.run_simulator(starting_sample_id, parameters, path_to_main_dir)
    
    
    # Again reformat values to fit with the rest of the chain
    values_new =[np.zeros(values.shape[0]) for k in range(values.shape[1]-1)]



    for n in range(values.shape[0]):
        for k in range(values.shape[1]-1):
            values_new[k][n] = values[n, k+1]
    
    values = values_new
    
    
    if(rank == 0):
        for k in range(len(values)):
            if args.output_append:
                if os.path.exists(args.output_values_files[k]):
                    previous_values = np.loadtxt(args.output_values_files[k])
        
                    new_values = np.zeros((values[k].shape[0] + previous_values.shape[0]))
        
                    new_values[:previous_values.shape[0]] = previous_values
                    new_values[previous_values.shape[0]:] = values[k]
        
                    values[k] = new_values
            np.savetxt(args.output_values_files[k], values[k])
