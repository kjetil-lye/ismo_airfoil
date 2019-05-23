# Airfoil ISMO run

All the commands should be run in the subfolder ```airfoil_chain```.

To run outside of Euler/LSF-clusters

    bash run_in_bash.sh

To just display the commands that would be run without running, do
 
    bash run_in_bash.sh --dry_run

To run on Euler/LSF do

    bash run_on_euler.sh

and again to only display the bsub commands that would be run do

    bash run_on_euler.sh --dry_run
