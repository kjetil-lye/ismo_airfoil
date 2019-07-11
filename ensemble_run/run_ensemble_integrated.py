import os
import shutil
import git
import copy
import sys
import subprocess
import glob
import ismo.submit
import multiprocessing

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

        newtun_paths = [f'{os.getcwd()}/nuwtun_solver/{p}' for p in newtun_folders]
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


def get_configuration_name(basename, iteration_sizes):
    return f'{basename}_iterations_{"_".join(map(str, iteration_sizes))}'



def run_configuration(*, basename,
                      reruns, 
                      number_of_processes,
                      iteration_sizes, 
                      repository_path, 
                      dry_run,
                      only_missing,
                      memory,
                      submitter,
                      generator):
    folder_name = get_configuration_name(basename, iteration_sizes)
    if not only_missing:
        os.mkdir(folder_name)
    with ChangeFolder(folder_name):
        if not only_missing:
            shutil.copytree(os.path.join(repository_path, 'nuwtun_solver'), 'nuwtun_solver')
            shutil.copytree(os.path.join(repository_path, 'airfoil_integrated'), 'airfoil_integrated')



        with PathForNuwtun():
            with ChangeFolder('airfoil_integrated'):
                iteration_sizes_as_str = [str(x) for x in iteration_sizes]
                command_to_submit_list = [sys.executable,
                                          'run_airfoil.py',
                                          '--number_of_samples_per_iteration',
                                          *iteration_sizes_as_str,
                                          '--number_of_processes',
                                          str(number_of_processes),
                                          '--retries',
                                          str(reruns),
                                          '--generator',
                                          generator,
                                          '--with_competitor',
                                          '--save_result'
                                  ]


                if only_missing:
                    should_run = all_successfully_completed()
                else:
                    should_run = True

                command = ismo.submit.Command(command_to_submit_list)

                submitter(command,
                          number_of_processes=number_of_processes,
                          wait_time_in_hours=120,
                          memory_limit_in_mb=memory)

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

    parser.add_argument('--max_processes', type=int, default=multiprocessing.cpu_count(),
                        help='Maximum number of processes')

    parser.add_argument('--batch_size_factors', type=float, nargs='+', default=[0.5, 1],
                        help='Batch sizes to use as a ratio of starting_size')


    repo = git.Repo(search_parent_directories=True)

    parser.add_argument('--repository_path', type=str, default=repo.working_dir,
                        help='Absolute path of the repository')

    parser.add_argument('--dry_run', action='store_true',
                        help='Only do a dry run, no jobs are submitted or run')

    parser.add_argument('--only_missing', action='store_true',
                        help='Only run missing configurations')
    
    
    parser.add_argument('--memory', type=int, default=8000,
                        help="Memory per process (in MB)")

    parser.add_argument('--submitter', type=str, default='bash',
                        help="Submitter (either bash or lsf)")

    parser.add_argument('--generator', type=str, default='monte-carlo',
                        help="Generator to use (either 'monte-carlo' or 'sobol')")


    args = parser.parse_args()
    submitter = ismo.submit.create_submitter(args.submitter, None, dry_run=args.dry_run)

    for starting_size in args.starting_sizes:
        for batch_size_factor in args.batch_size_factors:
            iteration_sizes = [starting_size]

            while sum(iteration_sizes) < args.compute_budget:
                iteration_sizes.append(int(batch_size_factor*starting_size))
            batch_size = iteration_sizes[-1]
            number_of_processes = min(args.max_processes, batch_size)
            run_configuration(basename=args.basename,
                              reruns=args.number_of_reruns,
                              iteration_sizes=iteration_sizes,
                              repository_path=args.repository_path,
                              dry_run=args.dry_run,
                              number_of_processes=number_of_processes,
                              only_missing=args.only_missing,
                              memory=args.memory,
                              submitter=submitter,
                              generator=args.generator)





