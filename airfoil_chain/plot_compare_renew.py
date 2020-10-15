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


     data_ismo = np.loadtxt(f'../results/ismo_airfoils_objective_{args.generator}_{args.compare_batch_size}_{args.compare_start_size}.txt')
     data_ismo_renew = np.loadtxt(f'../results_renew/ismo_airfoils_objective_{args.generator}_{args.compare_batch_size}_{args.compare_start_size}.txt')

     iterations_numbers = np.arange(0, data_ismo.shape[0])
     sample_per_iteration = np.ones_like(iterations_numbers)
     sample_per_iteration[0] = args.compare_start_size
     sample_per_iteration[1:] *= args.compare_batch_size

     work_per_iteration = np.cumsum(sample_per_iteration)


     plt.errorbar(work_per_iteration , np.mean(data_ismo, axis=1),
                  yerr=np.std(data_ismo, axis=1),  label='ISMO',
                  fmt='o', uplims=True, lolims=True)

     plt.errorbar(work_per_iteration , np.mean(data_ismo_renew, axis=1),
                 yerr=np.std(data_ismo_renew, axis=1),  label='ISMO reusing samples',
                 fmt='o', uplims=True, lolims=True)


     plt.title(f'Comparison ISMO with reusing samples ({args.generator})\nwith {args.compare_start_size} starting samples\nand {args.compare_batch_size} batch size.')
     plt.xscale('log', basex=2)
     plt.yscale('log', basey=2)
     plt.xlabel("Number of evaluations of the simulator")
     plt.ylabel("Minimum value")
     plot_info.plot_info.legendLeft()
     plot_info.savePlot(f"compare_with_ismo_reuse_mean_std_batch_size_{args.generator}_{args.compare_batch_size}_{args.compare_start_size}")
     plt.close('all')
