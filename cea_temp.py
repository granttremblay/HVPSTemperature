
#!/usr/bin/env python

"""
cea_temp.py: Plot the HRC Central Electronics Assembly temperature against pitch
"""

__author__ = "Dr. Grant R. Tremblay"
__license__ = "MIT"

import os
import sys

import time
import datetime as dt

from astropy.io import ascii
from astropy.table import vstack
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.dates import epoch2num

import numpy as np
from scipy import stats
#!/usr/bin/env python

"""
plotgoes.py: Plot the GOES rates
"""

__author__ = "Dr. Grant R. Tremblay"
__license__ = "MIT"

import os
import sys

import time
import datetime as dt

from astropy.io import ascii
from astropy.table import vstack
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.dates import epoch2num

import numpy as np
from scipy import stats



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

def parse_msid(msid_directory):

    print("Parsing MSIDs")

    temp_msid = ascii.read(msid_directory + "2CE00ATM_5min_lifetime.csv", format="fast_csv")
    hvpstemp_msid = ascii.read(msid_directory + "2IMHVATM_5min_lifetime.csv", format="fast_csv")

    pitch_msid = ascii.read(msid_directory + "Point_SunCentAng_5min_lifetime.csv", format="fast_csv")
    dist_msid = ascii.read(msid_directory + "Dist_SatEarth_5min_lifetime.csv", format="fast_csv")

    # The pitch is always populated, but the temperatures are only populated
    # when the HRC is taking data. So you need to use the pitch and distance
    # MSIDs as lookup tables, basically. Meaning you have to mask them!

    # Print a Boolean array where times are found to match
    densemask = np.in1d(pitch_msid['times'], temp_msid['times'])

    sparsemask = np.in1d(temp_msid['times'], pitch_msid['times'][densemask])
    hvps_sparsemask = np.in1d(hvpstemp_msid['times'], pitch_msid['times'][densemask])

    times = convert_chandra_time(temp_msid['times'][sparsemask])
    hvps_times = convert_chandra_time(hvpstemp_msid['times'][hvps_sparsemask])
    cea_temp = temp_msid['maxes'][sparsemask]
    hvps_temp = hvpstemp_msid['maxes'][hvps_sparsemask]
    pitch = pitch_msid['vals'][densemask]
    distance = dist_msid['vals'][densemask] / 1000.0
    # Factor of 1000 is to convert distance m ---> km


    data = {"CEA Times": times,
            "HVPS Times": times,
            "CEA Temperature": cea_temp,
            "HVPS Temperature": hvps_temp,
            "Pitch": pitch,
            "Distance": distance}

    print("MSIDs parsed")
    return data


def styleplots():
    plt.style.use('ggplot')

    labelsizes = 13

    plt.rcParams['font.size'] = labelsizes
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['axes.labelsize'] = labelsizes
    plt.rcParams['xtick.labelsize'] = labelsizes
    plt.rcParams['ytick.labelsize'] = labelsizes


def plot_temps(data):

    styleplots()

    fig, ax = plt.subplots(figsize=(12, 8))

    #ax.plot_date(data["Times"], data["CEA Temperature"], markersize=2.0, label="Maximum CEA Temperature (2CE00ATM)",
    #             rasterized=True)

    scattertimes = data["CEA Times"] / 365.2422
    hvps_scattertimes = data["HVPS Times"] / 365.2422

    plot = ax.scatter(scattertimes, data["CEA Temperature"], c=data["Pitch"], cmap='RdBu', vmin=0, vmax=180, label="BOTTOM SERIES: Maximum CEA Temperature (2CE00ATM)")

    plot = ax.scatter(hvps_scattertimes, data["HVPS Temperature"], c=data["Pitch"], cmap='RdBu', vmin=0, vmax=180, label="TOP SERIES: Maximum HVPS Temperature (2IMHVATM)")

    ax.set_ylabel("Temperature (C)")
    ax.set_xlabel("Date")

    ax.legend()

    cbar = plt.colorbar(plot)

    cbar.set_label("Solar Pitch (degrees)")

def plot_pitch(data):
    styleplots()

    fig, ax = plt.subplots(figsize=(12, 8))

    #ax.plot_date(data["Times"], data["CEA Temperature"], markersize=2.0, label="Maximum CEA Temperature (2CE00ATM)",
    #             rasterized=True)

    plot = ax.scatter(data["HVPS Temperature"], data["Pitch"], c=data["Distance"], cmap='plasma')

    ax.set_ylabel("Spacecraft Pitch (degrees)")
    ax.set_xlabel("Maximum HVPS Temperature (C)")

    ax.set_xlim(20, 50)

    cbar = plt.colorbar(plot)

    cbar.set_label("Spacecraft Altitude (km)")


def plot_pitch_dist(data):

    styleplots()

    fig, ax = plt.subplots(figsize=(12, 8))

    #ax.plot_date(data["Times"], data["CEA Temperature"], markersize=2.0, label="Maximum CEA Temperature (2CE00ATM)",
    #             rasterized=True)

    plot = ax.scatter(data["Pitch"], data["Distance"], c=data["CEA Temperature"], cmap='plasma')

    ax.set_ylabel("Spacecraft Altitude (km)")
    ax.set_xlabel("Pitch Angle (degrees)")

    cbar = plt.colorbar(plot)

    cbar.set_label("Maximum CEA Temperature (C)")



def main():

    msid_directory = "/Users/grant/Dropbox/HRCOps/MSIDCloud/"

    data = parse_msid(msid_directory)

    plot_temps(data)
    plot_pitch(data)
    #plot_pitch_dist(data)


if __name__ == '__main__':
    start_time = time.time()

    main()

    runtime = round((time.time() - start_time), 3)
    print("Finished in {} seconds".format(runtime))

    print("Showing Plots")
    plt.show()
