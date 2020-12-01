"""This code contains various functions to create RMS plots
from the Snakemake pipeline output (mainly from beam17 results)
"""

import numpy as np
import sys
import argparse
import logging

import dstack as ds

import matplotlib
import matplotlib.pyplot as plt

#=== RCparams for plotting ===
matplotlib.rcParams['xtick.direction'] = 'inout'
matplotlib.rcParams['ytick.direction'] = 'inout'

matplotlib.rcParams['xtick.major.size'] = 9
matplotlib.rcParams['ytick.major.size'] = 9

matplotlib.rcParams['xtick.major.width'] = 3
matplotlib.rcParams['ytick.major.width'] = 3

matplotlib.rcParams['axes.linewidth'] = 3

plt.rcParams['xtick.labelsize']=15
plt.rcParams['ytick.labelsize']=15

#4 sampled colors from viridis
c0 = '#440154';#Purple
c1 = '#30678D';#Blue
c2 = '#35B778';#Greenish
c3 = '#FDE724';#Yellow

outlier_color = 'dimgrey'


#=== Functions ===
def get_RMS_and_spectral_array_from_CIM(cim_path,chan=0,chan_max=None):
    """Create and return an array containing the RMS of the
    input Cim. Also, gets the corrsponding spectral axis

    Parameters
    ==========
    cim_path: str
        The path to the CASAimage

    Return
    ======
    rms_arr: numpy.ndarray
        RMS values for ecah channel
    spectral_arr: numpy.ndarray
        The frequency values for each array
    """

    rms_arr = ds.cim.measure_CIM_RMS(cim_path,all_dim=False,chan=chan,chan_max=chan_max)

    print(rms_arr)


if __name__ == "__main__":

    #get_RMS_and_spectral_array_from_CIM('/home/krozgonyi/Desktop/sandbox/stacked_grids/image.deep.restored',chan_max=8)
    get_RMS_and_spectral_array_from_CIM('/home/krozgonyi/Desktop/dstack_test_files/image.restored.wr.1.sim_PC',chan_max=4)