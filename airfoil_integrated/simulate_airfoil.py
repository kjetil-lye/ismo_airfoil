import numpy as np
import optimizer_interface as opi
def simulate_airfoil(*,
                     starting_sample_id,
                     parameters,
                     number_of_processes=1):
                     

    path_to_main_dir ='../nuwtun_solver/examples/coupled_with_solver'

    parameters_with_sample_id = np.zeros((parameters.shape[0],
                                          parameters.shape[1]+1))

    parameters_with_sample_id[:,1:] = parameters

    parameters_with_sample_id[:,0] = np.arange(starting_sample_id,
                                               starting_sample_id
                                               +parameters.shape[0])

    
    values = opi.run_simulator(starting_sample_id,
                               parameters_with_sample_id,
                               path_to_main_dir,
                               number_of_processes)

    return values
