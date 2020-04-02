import ismo
import ismo.submit
import ismo.submit.defaults
import os


class SeveralVariablesCommands(ismo.submit.defaults.Commands):
     def __init__(self, number_of_processes=1, **kwargs):
         super().__init__(**kwargs)

         self.current_sample_number = 0


         self.number_of_processes=number_of_processes

         self.preproccsed_filename_base = self.prefix + 'preprocessed_values.txt'
         self.simulated_output_filename_base = self.prefix + 'simulation_output.txt'

     def do_evolve(self, submitter,
                   *,
                   iteration_number: int,
                   input_parameters_file: str,
                   output_value_files: list):

         # Evolve
         evolve = ismo.submit.Command(['mpirun', '-np', 
                                       str(self.number_of_processes[iteration_number]),
                                       self.python_command,
                                       'simulate_airfoil.py'])
         
         evolve = evolve.with_long_arguments(input_parameters_file=input_parameters_file,
                                             output_values_files=output_value_files,
                                             iteration_number=iteration_number,
                                             starting_sample=self.current_sample_number)
         
         evolve = self.add_start_end_values(evolve)
         
         submitter(evolve, wait_time_in_hours=24, number_of_processes=self.number_of_processes[iteration_number])

         self.current_sample_number = self.number_of_samples_generated


if __name__ == '__main__':
    files_to_delete = ['parameters.txt', 'model_{}.h5', 'values_{}.txt',
                       'parameters_for_optimization.txt']
    
    for filename_template in files_to_delete:
        for component in range(3):
            filename = filename_template.format(component)
            if os.path.exists(filename):
                os.remove(filename)
            
    import argparse

    parser = argparse.ArgumentParser(description="""
Submits all the jobs for the sine experiments
        """)

    parser.add_argument('--number_of_processes', type=int, default=[1], nargs='+', required=True,
                        help='Number of processes to use (for MPI, only applies to simulation step)')

    parser.add_argument('--number_of_samples_per_iteration', type=int, nargs='+', required=True,
                        help='Number of samples per iteration')

    parser.add_argument('--chain_name', type=str, default="several",
                        help="Name of the chain to run")

    parser.add_argument('--generator', type=str, default="monte-carlo",
                        help="Generator to use (either 'monte-carlo' or 'sobol'")

    parser.add_argument('--submitter', type=str, required=True,
                        help='Submitter to be used. Either "bash" (runs without waiting) or "lsf"')

    parser.add_argument('--dry_run', action='store_true',
                        help="Don't actually run the command, only print the commands that are to be executed")

    parser.add_argument('--starting_sample', type=int, default=0,
                        help='The sample to start from')


    parser.add_argument('--container_type', type=str, default=None,
                        help="Container type (none, docker, singularity)")

    parser.add_argument('--container', type=str, default='docker://kjetilly/machine_learning_base:0.1.2',
                        help='Container name')

    args = parser.parse_args()

    submitter = ismo.submit.create_submitter(args.submitter, args.chain_name, dry_run=args.dry_run,
                            container_type=args.container_type,
                            container=args.container)

    number_of_processes = args.number_of_processes



    if len(number_of_processes) != 1 and len(number_of_processes) != len(args.number_of_samples_per_iteration):
        raise Exception(f"number_of_processes should either be a single number, or the same number as the number of iterations\n" +\
                        f"got {number_of_processes}, while number_of_samples_per_iteration was {args.number_of_samples_per_iteration}")

    elif len(number_of_processes) == 1:
        number_of_processes = [number_of_processes[0] for k in args.number_of_samples_per_iteration]

    commands = SeveralVariablesCommands(dimension=20,
                                        starting_sample=args.starting_sample,
                                        number_of_processes=number_of_processes,
                                        number_of_output_values=3,
                                        training_parameter_config_file='training_parameters.json',
                                        optimize_target_file='objective.py',
                                        optimize_target_class='Objective',
                                        python_command='python',
                                        objective_parameter_file='penalties.json',
                                        sample_generator_name=args.generator,
                                        output_append=True,
                                        reuse_model=True
                                        )

    chain = ismo.submit.Chain(args.number_of_samples_per_iteration, submitter,
                              commands=commands)

    chain.run()
    