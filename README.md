# Airfoil ISMO run

Clone with

    git clone --recursive git@github.com:kjetil-lye/ismo_airfoil.git

If you already cloned without the recursive option, do (from ```ismo_airfoil```):

    git submodule update --init --recursive

## Running in virtualenv

To make sure one has all the python packages required (and that one does not mess up ones python directory), one can use virtualenv. [First install it (for python3)](https://virtualenv.pypa.io/en/latest/installation/) :

    pip3 install --user virtualenv

or you can leave out the ```--user``` option if you want it to be available for all users.

Then create a new virutal environment ([see the documentation for what is going on](https://virtualenv.pypa.io/en/latest/userguide/)):

    virtualenv3 .venv

activate the environment

    source .venv/bin/activate

Then, *only for the first time*, install the needed packages (after doing ```souruce .venv/bin/activate```):

    pip install -r requirements.txt

Now you can run the commands below. To leave the virtual enviroment, use

    deactivate

which will give you back the ordinary shell.

In general, to use ```virutalenv``` from a new terminal window once you have the ```.venv``` setup, you do

    cd <path to ismo_airfoil>
    source .venv/bin/activate
    # Now you are in the virtual environemnt (promp should have a (.venv) in it)
    cd airfoil_chain
    bash run_in_bash.sh
    # do some more
    deactivate
   



## Running
All the commands should be run in the subfolder ```airfoil_chain```.

To run outside of Euler/LSF-clusters

    bash run_in_bash.sh

To just display the commands that would be run without running, do
 
    bash run_in_bash.sh --dry_run

To run on Euler/LSF do

    bash run_on_euler.sh

and again to only display the bsub commands that would be run do

    bash run_on_euler.sh --dry_run
