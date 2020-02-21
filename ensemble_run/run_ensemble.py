import os
import shutil
import git
import copy
import sys
import subprocess
import glob

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


def get_configuration_name(basename, rerun, iteration_sizes):
    return f'{basename}_rerun_{rerun}_iterations_{"_".join(map(str, iteration_sizes))}'



def run_configuration(*, basename, rerun, iteration_sizes, repository_path, dry_run, submitter_name, only_missing, container, container_type):
    folder_name = get_configuration_name(basename, rerun, iteration_sizes)
    if not only_missing:
        os.mkdir(folder_name)
    with ChangeFolder(folder_name):
        if not only_missing:
            shutil.copytree(os.path.join(repository_path, 'nuwtun_solver'), 'nuwtun_solver')
            shutil.copytree(os.path.join(repository_path, 'airfoil_chain'), 'airfoil_chain')



        with PathForNuwtun():
            with ChangeFolder('airfoil_chain'):
                starting_sample = rerun * sum(iteration_sizes)
                iteration_sizes_as_str = [str(x) for x in iteration_sizes]
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
                                  folder_name
                                  ]

                if container is not None:
                    command_to_run.extend(['--container', container])
                if container_type is not None:
                    command_to_run.extend(['--container_type', container_type])

                if dry_run:
                    command_to_run.append('--dry_run')

                if only_missing:
                    should_run = all_successfully_completed()
                else:
                    should_run = True

                if should_run:
                    subprocess.run(command_to_run, check=True)

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


    args = parser.parse_args()


    for starting_size in args.starting_sizes:
        for batch_size_factor in args.batch_size_factors:
            iteration_sizes = [starting_size]

            while sum(iteration_sizes) < args.compute_budget:
                iteration_sizes.append(int(batch_size_factor*starting_size))

            for rerun in range(args.number_of_reruns):
                run_configuration(basename=args.basename,
                                  rerun=rerun,
                                  iteration_sizes=iteration_sizes,
                                  repository_path=args.repository_path,
                                  dry_run=args.dry_run,
                                  submitter_name=args.submitter,
                                  only_missing=args.only_missing,
                                  container_type=args.container_type,
                                  container=args.container)





