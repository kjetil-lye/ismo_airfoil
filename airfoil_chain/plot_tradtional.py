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

     for sample_array in all_values:
         minimum_sample = cummin(sample_array)

         number_of_iterations = np.arange(0, minimum_sample.shape[0])

         plt.loglog(number_of_iterations, minimum_sample, basex=2, basey=2)
        
     plt.axvline(512, color='grey', linestyle='--')
     plt.axvline(256, color='green', linestyle='--')
     plt.axhline(0.55, color='green', linestyle='--')
     plt.axhline(0.45, color='grey', linestyle='--')
     plt.grid(True)
     plt.xlabel("Number of evaluations of the simulator")
     plt.ylabel("Minimum value")
     plt.title("Optimization using traditional algorithms\nGreen line is minimum of mean\ngrey is minimum of mean-std")
     plot_info.showAndSave("optimized_traditional")

     

