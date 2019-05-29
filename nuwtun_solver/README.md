# nuwtun solver
The code for the solver is taken from [here](https://bitbucket.org/cpraveen/nuwtun/src/master/).

## Compiling the code

Add the following lines to your `.bashrc` file

	export NUWTUN_HOME=<path-to-nuwtun-directory>
	PATH=$PATH:$NUWTUN_HOME/src-flo
	PATH=$PATH:$NUWTUN_HOME/src-grd
	PATH=$PATH:$NUWTUN_HOME/src-utl
	PATH=$PATH:$NUWTUN_HOME/py-wrap
	export PATH

	
and refresh the paths via 

	source ~/.bashrc
   
To compile the code and create the various executables, run the following commands from the `nuwtun_solver` directory

	cd src-flo
	# Create the executable nuwtun_flo
	make  
	cd ../src-grd
	# Create the executable to deform the geometry and 
	# evaluate airfoil area
	make deform area

## Running the code coupled with the optimizer

The script `optimizer_interface.py` in the directory `airfoil_chain` acts as an interface to setup the various samples and run the solver for a set of input parameters. The folder where the samples are save is 

	nuwtun_solver/examples/coupled_with_solver

