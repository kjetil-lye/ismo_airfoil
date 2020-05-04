import pickle
import numpy as np
import sys
import argparse
import plot_info
import matplotlib.pyplot as plt

if __name__ == '__main__':
     parser = argparse.ArgumentParser(description="""
     Plots the result of the traditional optimization
    """)

     args = parser.parse_args()

     lift_drag_area_filename = 'traditional_optimization_all_lift_drag_areas.pic'
     results_filename = 'traditional_optimization_all_optimization_results.pic'

     all_values_filename = 'traditional_optimization_all_values.pic'

     aux_variables = ['lift', 'drag', 'area']

     with open(all_values_filename, 'rb') as inputfile:
         all_values = pickle.load(inputfile)
     cummin = np.minimum.accumulate

     all_values_new = []
     for sample_array in all_values:
         if type(sample_array[0]) == list:
              for sample_array_sub in sample_array:
                   all_values_new.append(sample_array_sub)
         else:
              all_values_new.append(sample_array)
     all_values = all_values_new

     max_number_of_iterations = max(len(sample_array) for sample_array in all_values)


     #
     # for sample_array in all_values:
     #
     #     sample_array = np.array(sample_array)
     #     minimum_sample = cummin(sample_array)
     #
     #     number_of_iterations = np.arange(0, minimum_sample.shape[0])
     #
     #     plt.loglog(number_of_iterations, minimum_sample, basex=2, basey=2)
     #
     # plt.axvline(512, color='grey', linestyle='--')
     # plt.axvline(256, color='green', linestyle='--')
     # plt.axhline(0.55, color='green', linestyle='--')
     # plt.axhline(0.45, color='grey', linestyle='--')
     # plt.grid(True)
     # plt.xlabel("Number of evaluations of the simulator")
     # plt.ylabel("Minimum value")
     # plt.title("Optimization using traditional algorithms\nGreen line is minimum of mean\ngrey is minimum of mean-std")
     # plot_info.showAndSave("optimized_traditional_all_paths")



     min_value = min(min(sample_array) for sample_array in all_values)
     max_value = min(2, max(max(sample_array) for sample_array in all_values))


     bins = 100
     histograms = np.zeros((max_number_of_iterations, bins))
     mean_per_iteration = np.zeros(max_number_of_iterations)
     std_per_iteration = np.zeros(max_number_of_iterations)
     min_per_iteration = np.zeros(max_number_of_iterations)
     max_per_iteration = np.zeros(max_number_of_iterations)

     for iteration in range(max_number_of_iterations):
          samples = []
          for sample_array in all_values:
               if len(sample_array) > iteration:
                    samples.append(sample_array[iteration])
          histogram, edges = np.histogram(samples, bins=bins, range=(min_value, max_value))

          histograms[iteration, :] = histogram

          mean_per_iteration[iteration] = np.mean(samples)
          std_per_iteration[iteration] = np.std(samples)
          min_per_iteration[iteration] = np.min(samples)
          max_per_iteration[iteration] = np.max(samples)
     iterations_mesh, edges_mesh = np.meshgrid(np.arange(0, max_number_of_iterations),
                                               np.linspace(min_value, max_value, bins))

     plt.pcolormesh(iterations_mesh, edges_mesh, histograms.T)
     plt.colorbar()
     plt.xscale('log', basex=2)
     plt.yscale('log', basey=2)
     plt.xlabel("Number of evaluations of the simulator")
     plt.ylabel("Minimum value")
     plt.axvline(512, color='grey', linestyle='--')
     plt.axvline(256, color='green', linestyle='--')
     plt.axhline(0.55, color='green', linestyle='--')
     plt.axhline(0.45, color='grey', linestyle='--')
     plot_info.showAndSave("optimized_traditional_histograms")

     number_of_iterations = np.arange(0, max_number_of_iterations)
     #plt.fill_between(number_of_iterations, mean_per_iteration-std_per_iteration, mean_per_iteration+std_per_iteration)
     plt.fill_between(number_of_iterations, min_per_iteration,
                      max_per_iteration)
     plt.plot(number_of_iterations, mean_per_iteration)
     plt.ylim([min_value, max_value])
     plt.show()

