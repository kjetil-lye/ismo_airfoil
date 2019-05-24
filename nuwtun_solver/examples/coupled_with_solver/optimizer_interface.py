#!/usr/bin/env python
# Python wrapper for interfacing between optimizer and nuwtun
# Author: Deep Ray, EPFL
# Date  : 19 April, 2019

import os
import numpy as np

def create_samples(st,se,N,params,mdir):

    print ("  --- CREATING SAMPLE DIRECTORIES\n")
    # Check if necessary input files are available
    file_dir     = mdir + "/files"
    assert(os.path.isdir(mdir))
    assert(os.path.isdir(file_dir))

    for i in range(N):

        sample = st+i
        comline = 'rm -rf '+mdir+'/SAMPLE_'+str(sample)
        os.system(comline)
    
        comline = 'cp -r ' + file_dir + ' ' + mdir+'/SAMPLE_'+str(sample)
        os.system(comline)

        hh_param = rnd_transform(params[i, 1::], sample)
    
        np.savetxt(mdir+'/SAMPLE_'+str(sample)+'/shape.dat', hh_param, fmt='%.10e')
    
def launch_all(st,se,N,params,mdir):
    print ("  --- LAUNCHING JOBS:\n")
    cwd          = os.getcwd()

    for s in range(st, se+1):
    
        os.chdir(mdir+'/SAMPLE_'+str(s))
        
        comline = 'nuwtun_rae_pywrap.py input.param'
        #comline = 'bsub < job.sh'
        os.system(comline)
        
        os.chdir(cwd)
    
        print('      ...SAMPLE %d done' %(s))
    
def combine_data(st,se,N,params,mdir):

    print ("  --- COMBINING DATA\n")
    QoI = np.zeros((N, 4))
    for i in range(N):
        sample = st+i
        sdata_file = mdir+'/SAMPLE_'+str(sample)+'/sim_data.txt'
        QoI[i,0]   = sample
        QoI[i,1::] = np.loadtxt(sdata_file)
   
    return QoI

def rnd_transform(x,s): 
    m = len(x)
    for i in range(int(m/2)):
        x[i]     = 2*0.001*(i+1)*(x[i]-0.5)
        x[m-i-1] = 2*0.001*(i+1)*(x[m-i-1]-0.5)   
    return x


def run_simulator(sample_start, parameters, path_to_main):

    Nsamples   = parameters.shape[0]
    sample_end = sample_start + Nsamples - 1


    create_samples(sample_start,sample_end,Nsamples,parameters,path_to_main)
    launch_all(sample_start,sample_end,Nsamples,parameters,path_to_main)
    return combine_data(sample_start,sample_end,Nsamples,parameters,path_to_main)
