#!/usr/bin/env python
# Python wrapper for interfacing between optimizer and nuwtun
# Author: Deep Ray, EPFL
# Date  : 19 April, 2019

import os
import numpy as np
from mpi4py import MPI
import shutil
import subprocess

def create_sample(s, params, mdir):

    #print ("  --- CREATING SAMPLE DIRECTORY SAMPLE_%d\n" %s)
    # Check if necessary input files are available
    file_dir     = mdir + "/files"
    
    
    assert(os.path.isdir(mdir))
    assert(os.path.isdir(file_dir))

    
    shutil.rmtree('SAMPLE_'+str(s), ignore_errors=True)

    shutil.copytree(file_dir, f'SAMPLE_{s}')

    hh_param = rnd_transform(params[1::], params[0])
    
    np.savetxt('SAMPLE_'+str(s)+'/shape.dat', hh_param, fmt='%.10e')
    
def launch_solver(s, mdir):
    #print ("  --- LAUNCHING JOB FOR SAMPLE %d" %s )
    cwd = os.getcwd()

    os.chdir('SAMPLE_'+str(s))
        
    comline = 'nuwtun_rae_pywrap.py input.param'
    subprocess.run(comline.split(), check=True)
        
    os.chdir(cwd)
    
    #print('      ...SAMPLE %d done' %(s))
    
def combine_data(sample_offset, N, mdir, r):

    if(r == 0):
        print ("  --- COMBINING DATA\n")

    QoI = np.zeros((N, 4))
    for i in range(N):
        sample = sample_offset + i
        sdata_file ='SAMPLE_'+str(sample)+'/sim_data.txt'
        
        QoI[i, 0]   = sample
        QoI[i, 1::] = np.loadtxt(sdata_file)
    # Save space
    shutil.rmtree('SAMPLE_'+str(sample), ignore_errors=True)
    return QoI

def rnd_transform(x,s):
    m = len(x)
    for i in range(int(m/2)):
        x[i]     = 2*0.001*(i+1)*(x[i]-0.5)
        x[m-i-1] = 2*0.001*(i+1)*(x[m-i-1]-0.5)   
    return x


def run_simulator(sample_offset, parameters, path_to_main):

    Nsamples   = parameters.shape[0]

    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nproc = comm.Get_size()
    
    samples_per_proc = (Nsamples + nproc - 1) // nproc
    
    sample_index_start = rank * samples_per_proc
    sample_index_end = min(Nsamples, (rank+1)*samples_per_proc)

    if(rank==0):
        print ("\n  --- SIMULATING SAMPLES %d - %d\n" %(sample_offset,sample_offset+Nsamples-1))

    for sample_index in range(sample_index_start, sample_index_end):
        sample = sample_index + sample_offset
        assert(int(parameters[sample_index,0]) == sample)
        create_sample(sample, parameters[sample_index,:], path_to_main)
        launch_solver(sample, path_to_main)
    comm.barrier()
    if rank == 0:
        return combine_data(sample_offset, Nsamples, path_to_main, rank)
    else:
        return None
