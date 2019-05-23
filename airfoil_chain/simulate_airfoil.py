import numpy as np

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
Runs some complicated function on the input parameters
    """)

    parser.add_argument('--input_parameters_file', type=str, required=True,
                        help='Input filename for the parameters (readable by np.loadtxt)')

    parser.add_argument('--output_values_file', type=str, required=True,
                        help='Output filename for the values (will be written by np.savetxt)')

    parser.add_argument('--starting_sample', type=int, required=True,
                        help='The starting id of the first sample')

    parser.add_argument('--iteration_number', type=int, required=True,
                        help='The iteration number')

    


    args = parser.parse_args()
    starting_sample_id = args.starting_sample
    iteration_number = args.iteration_number
    
    parameters = np.loadtxt(args.input_parameters_file)

    values = np.zeros((parameters.shape[0], 4))

    for k in range(parameters.shape[0]):
        values[k,0] = k
        values[k,1] = np.sin(parameters[k,2]+parameters[k,0])
        values[k,2] = np.cos(parameters[k, 19] + parameters[k, 5])
        values[k,3] = np.tan(parameters[k, 4] + parameters[k, 8])

    np.savetxt(args.output_values_file, values)
