import os
import shutil
import git
import copy
import sys
import subprocess
import glob
import json
from ismo.submit import get_current_repository

def all_successfully_completed():
    lsf_files = glob.glob('lsf.o*')

    for lsf_filename in lsf_files:
        with open(lsf_filename) as f:
            content = f.read()


            if 'Successfully completed' not in content:
                return False

    return True

class PathForNuwtun:
    """
    Changes the path for Nuwtun
    """

    def __init__(self):
        pass

    def __enter__(self):
        self.old_path = copy.deepcopy(os.environ['PATH'])
        newtun_folders = ['src-flo',
                          'src-grd',
                          'src-utl',
                          'py-wrap']

        newtun_paths = [f'{get_current_repository()}/nuwtun_solver/{p}' for p in newtun_folders]
        newtun_added_path = ':'.join(newtun_paths)
        os.environ['PATH'] = f'{newtun_added_path}:{os.environ["PATH"]}'
    def __exit__(self, type, value, traceback):
        os.environ['PATH'] = self.old_path

class ChangeFolder:

    def __init__(self, folder):
        self.old_folder = os.getcwd()
        self.folder=folder

    def __enter__(self):

        os.chdir(self.folder)

    def __exit__(self, type, value, traceback):
        os.chdir(self.old_folder)


def get_configuration_name(basename, rerun, starting_size, batch_size_factor):
    return f'{basename}_rerun_{rerun}_iterations_{starting_size}_{float(batch_size_factor)}'



def run_configuration(*, basename, rerun, iteration_sizes, repository_path, dry_run, submitter_name, only_missing, container, container_type,
                      sample_generator):
    starting_size = iteration_sizes[0]
    batch_size_factor = iteration_sizes[0]/iteration_sizes[1]

    folder_name = get_configuration_name(basename, rerun, starting_size, batch_size_factor)
    if not only_missing or not os.path.exists(folder_name):
        os.mkdir(folder_name)
    with ChangeFolder(folder_name):
        if only_missing:
            should_run = not os.path.exists('airfoil_chain')
        if not only_missing or not os.path.exists('airfoil_chain'):
            shutil.copytree(os.path.join(repository_path, 'airfoil_chain'), 'airfoil_chain')



        with PathForNuwtun():
            with ChangeFolder('airfoil_chain'):
                starting_sample = rerun * sum(iteration_sizes)
                iteration_sizes_as_str = [str(int(x)) for x in iteration_sizes]
                
                for iteration_size in iteration_sizes:
                    if int(iteration_size) < 1:
                        raise Exception(f"Iteration size is 0, all iterations sizes: {iteration_sizes}")
                command_to_run = [sys.executable,
                                  'submit_airfoil.py',
                                  '--number_of_samples_per_iteration',
                                  *iteration_sizes_as_str,
                                  '--number_of_processes',
                                  *iteration_sizes_as_str,
                                  '--submitter',
                                  submitter_name,
                                  '--starting_sample',
                                  str(starting_sample),
                                  '--chain_name',
                                  folder_name,
                                  '--generator',
                                  sample_generator
                                  ]

                if container is not None:
                    command_to_run.extend(['--container', container])
                if container_type is not None:
                    command_to_run.extend(['--container_type', container_type])

                if dry_run:
                    command_to_run.append('--dry_run')

                if only_missing:
                    should_run = should_run or not all_successfully_completed()
                else:
                    should_run = True

                if should_run:
                    subprocess.run(command_to_run, check=True)
                    
def get_competitor_basename(basename):
    return f'{basename}_competitor'

def get_iteration_sizes(starting_size, batch_size_factor, compute_budget):
    iteration_sizes = [starting_size]

    while sum(iteration_sizes) < compute_budget:
        iteration_sizes.append(int(batch_size_factor * starting_size))

    return iteration_sizes

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="""
Runs the ensemble for M different runs (to get some statistics)./

""")

    parser.add_argument('--number_of_reruns', type=int, default=10,
                        help='Total number of reruns to get the ensemble')


    parser.add_argument('--basename', type=str, default='ensemble_run',
                        help='Basename for the ensemble')

    parser.add_argument('--compute_budget', type=int, default=512,
                        help='Maximum compute budget (in terms of number of samples that can be computed from simulator)')

    parser.add_argument('--starting_sizes', type=int, nargs='+', default=[16, 32, 64],
                        help='Starting sizes to use')

    parser.add_argument('--batch_size_factors', type=float, nargs='+', default=[0.25, 0.5, 1],
                        help='Batch sizes to use as a ratio of starting_size')


    repo = git.Repo(search_parent_directories=True)

    parser.add_argument('--repository_path', type=str, default=repo.working_dir,
                        help='Absolute path of the repository')

    parser.add_argument('--dry_run', action='store_true',
                        help='Only do a dry run, no jobs are submitted or run')

    parser.add_argument('--submitter', type=str, default='lsf',
                        help='Name of submitter to use, can be lsf or bash')

    parser.add_argument('--only_missing', action='store_true',
                        help='Only run missing configurations')


    parser.add_argument('--container_type', type=str, default=None,
                        help="Container type (none, docker, singularity)")

    parser.add_argument('--container', type=str, default='docker://kjetilly/machine_learning_base:0.1.2',
                        help='Container name')

    parser.add_argument('--generator', type=str, default="monte-carlo",
                        help="Generator to use (either 'monte-carlo' or 'sobol'")
                        



    args = parser.parse_args()


    # Save configuration for easy read afterwards
    with open("ensemble_setup.json", 'w') as f:
        json.dump(vars(args), f, indent=4)

    
    # This will be to store the competitors afterwards
    all_sample_sizes = []
    
    # Loop through configurations
    for starting_size in args.starting_sizes:
        for batch_size_factor in args.batch_size_factors:

            iteration_sizes = get_iteration_sizes(starting_size, batch_size_factor, args.compute_budget)

            for rerun in range(args.number_of_reruns):
                run_configuration(basename=args.basename,
                                  rerun=rerun,
                                  iteration_sizes=iteration_sizes,
                                  repository_path=args.repository_path,
                                  dry_run=args.dry_run,
                                  submitter_name=args.submitter,
                                  only_missing=args.only_missing,
                                  container_type=args.container_type,
                                  container=args.container,
                                  sample_generator=args.generator)
            
            
            for iteration_number, iteration_size in enumerate(iteration_sizes):
                
                number_of_samples = sum(iteration_sizes[:iteration_number + 1])
                all_sample_sizes.append(number_of_samples)
                
    
    # Make sure we do not have duplications
    all_sample_sizes = set(all_sample_sizes)
    
    # Run competitors
    for sample_size in all_sample_sizes:
        for rerun in range(args.number_of_reruns):
            run_configuration(basename=get_competitor_basename(args.basename),
                                  rerun=rerun,
                                  # First is the number of points we will use to 
                                  # train, second is the number that will be 
                                  # evaluated. Our whole budget is sample_size//2,
                                  # so we evaluate half at the samples for training,
                                  # and then use the rest to optimize/evaluate the resulting
                                  # optimized points
                                  iteration_sizes=[sample_size//2, sample_size//2],
                                  repository_path=args.repository_path,
                                  dry_run=args.dry_run,
                                  submitter_name=args.submitter,
                                  only_missing=args.only_missing,
                                  container_type=args.container_type,
                                  container=args.container,
                                  sample_generator=args.generator)
            
                    
                





