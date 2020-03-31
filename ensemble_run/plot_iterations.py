"""
Runs all configuration for analysis
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os
import subprocess
import ismo.submit
import json
import plot_info
import collections
from run_ensemble import get_configuration_name, get_iteration_sizes, get_competitor_basename

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage:\n\tpython {} <name of python script> <compute budget> <other arguments passed to python script>".format(sys.argv[0]))
        print("<compute budget> should be in terms of number of total samples calculated (integer). Reruns not included.")
        exit(1)
    python_script = sys.argv[1]
    compute_budget = int(sys.argv[2])

    with open('ensemble_setup.json') as f:
        configuration = json.load(f)

    for generator in [configuration['generator']]:

        for starting_size in configuration['starting_sizes']:
            for batch_size_factor in configuration['batch_size_factors']:

                starting_sample=0
                iterations = get_iteration_sizes(starting_size, batch_size_factor, configuration['compute_budget'])
                
                number_of_reruns = configuration['number_of_reruns']
                
                min_value_per_iteration = np.zeros((len(iterations), number_of_reruns))
                for rerun in range(number_of_reruns):
                    output_folder = get_configuration_name(configuration['basename'],
                                                           rerun, starting_size, batch_size_factor)
                    for iteration in range(len(iterations)):

                        try:
                            output_objective = os.path.join(output_folder,
                                                         f'objective.txt')
                            start_index = sum(iterations[:iteration])
                            end_index = sum(iterations[:iteration + 1])
                            values = np.loadtxt(output_objective)[start_index:end_index]
                            values = values[~np.isnan(values)]
                            min_value = np.min(values)
                            if iteration > 0:
                                min_value = min(min_value, np.min(min_value_per_iteration[:iteration,rerun]))
    
                            min_value_per_iteration[iteration, rerun] = min_value
                        except:
                             print(f"Failing {batch_size_factor} {starting_size} {generator}")

                min_value_per_iteration_competitor = np.zeros((len(iterations), number_of_reruns))
                for rerun in range(number_of_reruns):

                    for iteration in range(len(iterations)):
                        try:
                            all_values = []
                            
                            number_of_samples = sum(iterations[:iteration+1])
                            
                            competitor_basename = get_competitor_basename(configuration['basename'])
                            output_folder = get_configuration_name(configuration['basename'],
                                                           rerun, number_of_samples//2,
                                                           1)
                            
                            output_objective = os.path.join(output_folder,
                                                     f'objective.txt')
    
                            values = np.loadtxt(output_objective)
                            
                            assert(values.shape[0] == number_of_samples)
                            values = values[~np.isnan(values)]
                            all_values.extend(values)
    
    
                            min_value = np.min(all_values)
    
                            min_value_per_iteration_competitor[iteration, rerun] = min_value
                        except:
                            print(f"Failing {batch_size_factor} {starting_size} {generator}")

                iteration_range = np.arange(0, len(iterations))
                plt.errorbar(iteration_range, np.mean(min_value_per_iteration, 1),
                             yerr=np.std(min_value_per_iteration, 1), label='ISMO',
                             fmt='o', uplims=True, lolims=True)



                plt.errorbar(iteration_range+1, np.mean(min_value_per_iteration_competitor, 1),
                             yerr=np.std(min_value_per_iteration_competitor, 1), label='DNN+Opt',
                             fmt='*', uplims=True, lolims=True)

                print("#"*80)
                print(f"starting_size = {starting_size}, batch_size_factor = {batch_size_factor}")
                print(f"mean(ismo)={np.mean(min_value_per_iteration, 1)}\n"
                      f" var(ismo)={np.mean(min_value_per_iteration, 1)}\n"
                      f"\n"
                      f"mean(dnno)={np.mean(min_value_per_iteration_competitor, 1)}\n"
                      f" var(dnno)={np.mean(min_value_per_iteration_competitor, 1)}\n")

                plt.xlabel("Iteration $k$")
                plt.ylabel("$\\mathbb{E}( J(x_k^*))$")
                plt.legend()
                plt.title("script: {}, generator: {}, batch_size_factor: {},\nstarting_size: {}".format(
                    python_script, generator, batch_size_factor, starting_size))
                plot_info.savePlot("{script}_objective_{generator}_{batch_size}_{starting_size}".format(
                    script=python_script.replace(".py", ""),
                    batch_size=iterations[1],
                    starting_size=starting_size,
                    generator=generator))
                plt.close('all')


