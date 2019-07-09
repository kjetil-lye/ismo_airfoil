import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import numpy as np
import ismo.iterative_surrogate_model_optimization
import ismo.train.trainer_factory
import ismo.train.multivariate_trainer
import ismo.samples.sample_generator_factory
import ismo.optimizers
import matplotlib.pyplot as plt
import plot_info
from simulate_airfoil import simulate_airfoil
from objective import Objective

class SimulatorRunner:
    def __init__(self, number_of_processes, starting_sample):
        self.number_of_processes = number_of_processes
        self.starting_sample = starting_sample
        
    def __call__(self, x):
        y = simulate_airfoil(starting_sample_id=self.starting_sample,
                         parameters=x,
                         number_of_processes = self.number_of_processes)

        self.starting_sample += x.shape[0]

        return y
        

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
Runs the airfoil experiment
        """)

    parser.add_argument('--number_of_samples_per_iteration', type=int, nargs='+', default=[16, 4, 4, 4, 4, 4],
                        help='Number of samples per iteration')

    parser.add_argument('--generator', type=str, default='monte-carlo',
                        help='Generator')

    parser.add_argument('--simple_configuration_file', type=str, default='training_parameters.json',
                        help='Configuration of training and network')

    parser.add_argument('--optimizer', type=str, default='L-BFGS-B',
                        help='Configuration of training and network')

    parser.add_argument('--retries', type=int, default=1,
                        help='Number of retries (to get mean/variance). This option is studying how well it works over multiple runs.')

    parser.add_argument('--save_result', action='store_true',
                        help='Save the result to file')

    parser.add_argument('--prefix', type=str, default="airfoil_experiment_",
                        help="Prefix to all filenames")
    parser.add_argument('--number_of_processes', type=int, default=1,
                        help="Number of processes to use")

    parser.add_argument('--with_competitor', action='store_true',
                        help='Also run the standard DNN+Opt competitor to see how well ISMO is doing in comparison')

    objective = Objective()

    dimension = 20
    number_of_variables = 3 # lift drag area
    args = parser.parse_args()
    prefix = args.prefix


    all_values_min = []

    samples_as_str = "_".join(map(str, args.number_of_samples_per_iteration))
    for try_number in range(args.retries):
        print(f"try_number: {try_number}")
        generator = ismo.samples.create_sample_generator(args.generator)

        optimizer = ismo.optimizers.create_optimizer(args.optimizer)

        trainer = ismo.train.MultiVariateTrainer(
            [ismo.train.create_trainer_from_simple_file(args.simple_configuration_file) for _ in range(number_of_variables)])

        starting_sample = try_number*sum(args.number_of_samples_per_iteration)
        parameters, values = ismo.iterative_surrogate_model_optimization(
            number_of_samples_per_iteration=args.number_of_samples_per_iteration,
            sample_generator=generator,
            trainer=trainer,
            optimizer=optimizer,
            simulator=SimulatorRunner(args.number_of_processes,starting_sample),
            objective_function=objective,
            dimension=dimension,
            starting_sample=starting_sample
        )

        per_iteration = []
        total_number_of_samples = 0
        for number_of_samples in args.number_of_samples_per_iteration:
            total_number_of_samples += number_of_samples
            per_iteration.append(np.min(values[:total_number_of_samples]))
        all_values_min.append(per_iteration)

        if args.save_result:
            np.savetxt(f'{prefix}parameters_{try_number}_samples_{samples_as_str}.txt', parameters)
            np.savetxt(f'{prefix}values_{try_number}_samples_{samples_as_str}.txt', values)

    if args.with_competitor:
        competitor_min_values = np.zeros((args.retries, len(args.number_of_samples_per_iteration)-1))
        for try_number in range(args.retries):
            
            print(f"try_number (competitor): {try_number}")
            
            for iteration_number, number_of_samples_post in enumerate(args.number_of_samples_per_iteration[1:]):
                number_of_samples = sum(args.number_of_samples_per_iteration[:iteration_number+1])
                generator = ismo.samples.create_sample_generator(args.generator)
        
                optimizer = ismo.optimizers.create_optimizer(args.optimizer)
        
                trainer = ismo.train.MultiVariateTrainer(
                    [ismo.train.create_trainer_from_simple_file(args.simple_configuration_file) for _ in range(number_of_variables)])

                starting_sample = try_number*(number_of_samples_post+number_of_samples)
                parameters, values = ismo.iterative_surrogate_model_optimization(
                    number_of_samples_per_iteration=[number_of_samples, number_of_samples_post],
                    sample_generator=generator,
                    trainer=trainer,
                    optimizer=optimizer,
                    simulator=SimulatorRunner(args.number_of_processes, starting_sample),
                    objective_function=objective,
                    dimension=dimension,
                    starting_sample=starting_sample
                )
        
                competitor_min_values[try_number, iteration_number] = np.min(values)
    
                if args.save_result:
                    np.savetxt(f'{prefix}competitor_parameters_{try_number}_it_{iteration_number}_samples_{samples_as_str}.txt', parameters)
                    np.savetxt(f'{prefix}competitor_values_{try_number}_it_{iteration_number}_samples_{samples_as_str}.txt', values)
    
            
        
    print("Done!")
    iterations = np.arange(0, len(args.number_of_samples_per_iteration))
    plt.errorbar(iterations, np.mean(all_values_min,0), 
                 yerr=np.std(all_values_min,0), fmt='o',
                 label='ISMO')
    
    if args.with_competitor:
        plt.errorbar(iterations[:-1], np.mean(competitor_min_values,0), 
                 yerr=np.std(competitor_min_values,0), fmt='*',
                 label='DNN+Opt')
    plt.legend()
    plt.xlabel('Iteration')
    plt.ylabel('Min value')
    
    plot_info.savePlot(f'{prefix}optimized_value_{samples_as_str}')
