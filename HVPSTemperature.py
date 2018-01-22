#!/usr/bin/env python

"""
HVPSTemperature.py: Plot the HVPS temp over the mission lifetime
"""

__author__ = "Dr. Grant R. Tremblay"
__license__ = "MIT"

import os
import sys

import time
import datetime as dt

from astropy.io import ascii
from astropy.table import Table
from astropy.table import vstack

import numpy as np

from scipy.signal import argrelmax

import matplotlib.pyplot as plt
from matplotlib.dates import epoch2num

import numpy as np
from scipy import stats



def parse_msids(msid_directory):
    """
    Parse the CSV files for the MSDIs relevant to this study.
    I have already fetched these on the HEAD network using ska_fetch.
    """

    sphvatm = ascii.read(msid_directory + "2SPHVATM_5min_lifetime.csv", format="fast_csv")
    imhvatm = ascii.read(msid_directory + "2IMHVATM_5min_lifetime.csv", format="fast_csv")


    sphvatm_full = ascii.read(msid_directory + "2SPHVATM_full_pastyear.csv", format="fast_csv")
    imhvatm_full = ascii.read(msid_directory + "2IMHVATM_full_pastyear.csv", format="fast_csv")

    sp_temp = sphvatm['maxes']
    sp_temp_times = convert_chandra_time(sphvatm['times'])

    im_temp = imhvatm['maxes']
    im_temp_times = convert_chandra_time(imhvatm['times'])

    sp_temp_full = sphvatm_full['vals']
    sp_temp_times_full = convert_chandra_time(sphvatm_full['times'])

    im_temp_full = imhvatm_full['vals']
    im_temp_times_full = convert_chandra_time(imhvatm_full['times'])

    print("MSIDs parsed")
    return sp_temp, sp_temp_times, im_temp, im_temp_times, sp_temp_full, sp_temp_times_full, im_temp_full, im_temp_times_full



def convert_chandra_time(rawtimes):
    """
    Convert input CXC time (sec) to the time base required for the matplotlib
    plot_date function (days since start of the Year 1 A.D - yes, really).
    :param times: iterable list of times, in units of CXCsec (sec since 1998.0)
    :rtype: plot_date times (days since Year 1 A.D.)
    """

    # rawtimes is in units of CXC seconds, or seconds since 1998.0
    # Compute the Delta T between 1998.0 (CXC's Epoch) and 1970.0 (Unix Epoch)

    seconds_since_1998_0 = rawtimes[0]

    cxctime = dt.datetime(1998, 1, 1, 0, 0, 0)
    unixtime = dt.datetime(1970, 1, 1, 0, 0, 0)

    # Calculate the first offset from 1970.0, needed by matplotlib's plotdate
    # The below is equivalent (within a few tens of seconds) to the command
    # t0 = Chandra.Time.DateTime(times[0]).unix
    delta_time = (cxctime - unixtime).total_seconds() + seconds_since_1998_0

    plotdate_start = epoch2num(delta_time)

    # Now we use a relative offset from plotdate_start
    # the number 86,400 below is the number of seconds in a UTC day

    chandratime = (np.asarray(rawtimes) -
                   rawtimes[0]) / 86400. + plotdate_start

    return chandratime


def parse_events(mission_events_directory):
    """
    Parse mission events from the KADI database.
    """
    ascii.read(mission_events_directory + 'scs107s.csv')

    scs107s = ascii.read(mission_events_directory + 'scs107s.csv')

    scs107times = convert_chandra_time(scs107s['tstart'])

    print("There have been {} executions of SCS 107 due to high radiation".format(
        len(scs107times)))

    return scs107times


def styleplots():
    plt.style.use('ggplot')

    labelsizes = 13

    plt.rcParams['font.size'] = labelsizes
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = labelsizes
    plt.rcParams['xtick.labelsize'] = labelsizes
    plt.rcParams['ytick.labelsize'] = labelsizes


def main():


    # 2SPHVATM 5min
    # SIMHVATM 5min


    msid_directory = "/Users/grant/Dropbox/HRCOps/MSIDCloud/"
    mission_events_directory = './mission_events/'

    #master_table = parse_ace_archive(ace_data_directory)

    #acetime = convert_ace_time(master_table)
    #estrate = estimate_shield_rate(master_table)

    sp_temp, sp_temp_times, im_temp, im_temp_times, sp_temp_full, sp_temp_times_full, im_temp_full, im_temp_times_full = parse_msids(msid_directory)

    styleplots()

    fig, ax = plt.subplots(figsize=(12, 8))


    #ax.plot_date(acetime, estrate, '-', color='gray', lw=0.5, alpha=0.8)
    ax.plot_date(sp_temp_times, sp_temp, markersize=1.0,
                 label='SP HVPS Temperature (2SPHVATM)')

    ax.plot_date(im_temp_times, im_temp, markersize=1.0,
                     label='IM HVPS Temperature (2IMHVATM)')

    #ax.plot_date(sp_temp_times_full, sp_temp_full, markersize=1.0, label='SP HVPS Temperature (2SPHVATM)')

    #ax.plot_date(im_temp_times_full, im_temp_full, markersize=1.0, label='IM HVPS Temperature (2IMHVATM)')

    #ax.plot_date(fast_rise_rates, fast_rise_times, markersize=1.0, label='test')
    #ax.plot_date(dettimes, detrate, markersize=1.0, label='Detector Rate')

    #ax.set_yscale('log')
    ax.set_ylim(20, 42)
    ax.set_ylabel(r'HVPS Temperature (c)')
    ax.set_xlabel('Date')

    ax.legend()

    plt.show()


if __name__ == '__main__':
    start_time = time.time()

    main()

    runtime = round((time.time() - start_time), 3)
    print("Finished in {} seconds".format(runtime))
