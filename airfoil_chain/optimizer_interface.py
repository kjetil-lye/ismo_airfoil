#!/usr/bin/env python
# Python wrapper for interfacing between optimizer and nuwtun
# Author: Deep Ray, EPFL
# Date  : 19 April, 2019

import os
import numpy as np
from mpi4py import MPI


def create_sample(s, params, mdir):

    #print ("  --- CREATING SAMPLE DIRECTORY SAMPLE_%d\n" %s)
    # Check if necessary input files are available
    file_dir     = mdir + "/files"
    assert(os.path.isdir(mdir))
    assert(os.path.isdir(file_dir))

    comline = 'rm -rf '+mdir+'/SAMPLE_'+str(s)
    os.system(comline)
    
    comline = 'cp -r ' + file_dir + ' ' + mdir+'/SAMPLE_'+str(s)
    os.system(comline)

    hh_param = rnd_transform(params[1::], params[0])
    
    np.savetxt(mdir+'/SAMPLE_'+str(s)+'/shape.dat', hh_param, fmt='%.10e')
    
def launch_solver(s, mdir):
    #print ("  --- LAUNCHING JOB FOR SAMPLE %d" %s )
    cwd = os.getcwd()

    os.chdir(mdir+'/SAMPLE_'+str(s))
        
    comline = 'nuwtun_rae_pywrap.py input.param'
    os.system(comline)
        
    os.chdir(cwd)
    
    #print('      ...SAMPLE %d done' %(s))
    
def combine_data(st, N, mdir, r):

    if(r == 0):
        print ("  --- COMBINING DATA\n")

    QoI = np.zeros((N, 4))
    for i in range(N):
        sample = st+i
        sdata_file = mdir+'/SAMPLE_'+str(sample)+'/sim_data.txt'
        QoI[i, 0]   = sample
        QoI[i, 1::] = np.loadtxt(sdata_file)
   
    return QoI

def rnd_transform(x,s):
    m = len(x)
    for i in range(int(m/2)):
        x[i]     = 2*0.001*(i+1)*(x[i]-0.5)
        x[m-i-1] = 2*0.001*(i+1)*(x[m-i-1]-0.5)   
    return x


def run_simulator(sample_start, parameters, path_to_main):

    Nsamples   = parameters.shape[0]

    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nproc = comm.Get_size()

    assert(Nsamples == nproc)

    if(rank==0):
        print ("\n  --- SIMULATING SAMPLES %d - %d\n" %(sample_start,sample_start+Nsamples-1))

    for i in range(nproc):

        if(i==rank):
            sample = sample_start+i
            assert(int(parameters[i,0]) == sample)
            create_sample(sample, parameters[i,:], path_to_main)
            launch_solver(sample, path_to_main)
    comm.barrier()

    return combine_data(sample_start, Nsamples, path_to_main, rank)
