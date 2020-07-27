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

     parser.add_argument('--compare_start_size', type=int, default=64,
                         help="Starting size for comparison set")

     parser.add_argument('--compare_batch_size', type=int, default=16,
                         help="Batch size for comparison set")

     parser.add_argument('--generator', type=str, default="montecarlo",
                         help="Generator")


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


     all_minimum_values = []
     for sample_array in all_values:
     #
         sample_array = np.array(sample_array)
         minimum_sample = cummin(sample_array)
         all_minimum_values.append(minimum_sample)
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
          for sample_array in all_minimum_values:
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
     #plt.fill_between(number_of_iterations, mean_per_iteration-std_per_iteration, mean_per_iteration+std_per_iteration,
     #                alpha=0.5, color='C1', label=r'mean $\pm$ std')
     plt.fill_between(number_of_iterations, min_per_iteration,
                      max_per_iteration, alpha=0.5, color='C1', label=r'min-max')
     plt.plot(number_of_iterations, mean_per_iteration, label='mean')
     #plt.ylim([min_value, 4*max_value])
     plt.axvline(512, color='grey', linestyle='--')
     plt.axvline(256, color='green', linestyle='--')
     plt.axhline(0.55, color='green', linestyle='--')
     plt.axhline(0.45, color='grey', linestyle='--')
     plt.xscale('log', basex=2)
     plt.yscale('log', basey=2)
     plt.xlabel("Number of evaluations of the simulator")
     plt.ylabel("Minimum value")
     plot_info.plot_info.legendLeft()
     plot_info.showAndSave("optimized_traditional_mean_std")
     plt.close('all')

     

     data_ismo = np.loadtxt(f'../results/ismo_airfoils_objective_{args.generator}_{args.compare_batch_size}_{args.compare_start_size}.txt')

     iterations_numbers = np.arange(0, data_ismo.shape[0])

     print(iterations_numbers)

     sample_per_iteration = np.ones_like(iterations_numbers)
     sample_per_iteration[0] = args.compare_start_size
     sample_per_iteration[1:] *= args.compare_batch_size

     work_per_iteration = np.cumsum(sample_per_iteration)

     plt.errorbar(work_per_iteration, np.mean(data_ismo, axis=1),
                  yerr=np.std(data_ismo, axis=1),  label='ISMO',
                  fmt='o', uplims=True, lolims=True)


     mean_traditional_per_batch = []#np.zeros_like(iterations_numbers, dtype=np.float64)
     std_traditional_per_batch = []#np.zeros_like(iterations_numbers, dtype=np.float64)
     
     work_traditional = []
     
     for iteration_number in iterations_numbers:
          starting_iteration = work_per_iteration[iteration_number]
          
          samples = []
          for sample_array in all_minimum_values:
               if len(sample_array) > starting_iteration:
                    samples.append(sample_array[starting_iteration])
          if len(samples) == 0:
              print(f"iteration failing: {iteration_number}")
        
          #mean_traditional_per_batch[iteration_number] = np.mean(samples)
          #std_traditional_per_batch[iteration_number] = np.std(samples)
          
          mean_traditional_per_batch.append(np.mean(samples))
          std_traditional_per_batch.append(np.std(samples))
          work_traditional.append(starting_iteration)

     # Append additional samples
     current_work = work_traditional[-1]
     works = sorted([len(sample_array) for sample_array in all_minimum_values])
     
     while 2*current_work < works[-1]:
         current_work = 2*current_work
         
         samples = []
         for sample_array in all_minimum_values:
               if len(sample_array) > current_work:
                    samples.append(sample_array[current_work])
                    
         mean_traditional_per_batch.append(np.mean(samples))
         std_traditional_per_batch.append(np.std(samples))
         work_traditional.append(current_work)

     print(mean_traditional_per_batch)
     plt.errorbar(work_traditional, mean_traditional_per_batch,
                  yerr=std_traditional_per_batch,  label='TNC',
                  fmt='x', uplims=True, lolims=True)

     plt.title(f'Comparison with ISMO ({args.generator})\nwith {args.compare_start_size} starting samples\nand {args.compare_batch_size} batch size.')
     plt.xscale('log', basex=2)
     plt.yscale('log', basey=2)
     plt.xlabel("Number of evaluations of the simulator")
     plt.ylabel("Minimum value")
     plot_info.plot_info.legendLeft()
     plot_info.showAndSave("compare_with_ismo_optimized_traditional_mean_std")
     plt.close('all')


     plt.plot(work_per_iteration, np.mean(data_ismo, axis=1), '-o',
                  label='ISMO'
                  )

     
     plt.plot(work_traditional, mean_traditional_per_batch, '-x',
              label='TNC')

     plt.title(f'Comparison with ISMO ({args.generator})\nwith {args.compare_start_size} starting samples\nand {args.compare_batch_size} batch size.')
     plt.xscale('log', basex=2)
     plt.yscale('log', basey=2)
     plt.xlabel("Number of evaluations of the simulator")
     plt.ylabel("Minimum value")
     plot_info.plot_info.legendLeft()
     plot_info.showAndSave("compare_with_ismo_optimized_traditional_mean")
     plt.close('all')


