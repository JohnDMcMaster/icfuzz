from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import time
from picoscope import ps6000
import pylab as plt
import numpy as np
import json


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('fout',  help='Output')
    args = parser.parse_args()
    n = 64

    fout = open(args.fout, 'w')
    
    print("Checking for devices")
    ps = ps6000.PS6000(connect=False)
    allSerialNumbers = ps.enumerateUnits()
    assert len(allSerialNumbers) == 1, "Device not found"
    serial = allSerialNumbers[0]
    print("Connecting to PS6000 %s" % serial)
    ps = ps6000.PS6000(serial)

    print("Found the following picoscope:")
    print(ps.getAllUnitInfo())
    print()

    '''
    waveform_desired_duration = 50E-6
    obs_duration = 3 * waveform_desired_duration
    sampling_interval = obs_duration / 4096
    '''
    sampling_interval = 1e-6
    # in seconds
    obs_duration = 0.025
    (actualSamplingInterval, nSamples, maxSamples) = \
        ps.setSamplingInterval(sampling_interval, obs_duration)
    print("Sampling interval = %f ns" % (actualSamplingInterval * 1E9))
    print("Taking  samples = %d" % nSamples)
    print("Maximum samples = %d" % maxSamples)

    # the setChannel command will chose the next largest amplitude
    channelRange = ps.setChannel('A', 'DC', 2.0, 0.0, enabled=True, BWLimited=False)
    print("A Chosen channel range = %d" % channelRange)

    channelRange = ps.setChannel('C', 'DC', 5.0, 0.0, enabled=True, BWLimited=False)
    print("C Chosen channel range = %d" % channelRange)

    channelRange = ps.setChannel('D', 'DC', 5.0, 0.0, enabled=True, BWLimited=False)
    print("D Chosen channel range = %d" % channelRange)

    ps.setSimpleTrigger('D', 3.172, 'Rising', timeout_ms=10000, enabled=True)

    print('Run 1')
    ps.runBlock()
    ps.waitReady()
    # I don't have AWG
    print("Waiting for awg to settle.")
    #time.sleep(2.0)
    time.sleep(0.2)

    loopi = 0
    while True:
        if loopi >= n:
            break
        print('Loop %u' % loopi)
        ps.runBlock()
        ps.waitReady()
        print("Done waiting for trigger")
    
        dataA = ps.getDataV('A', nSamples, returnOverflow=False)
        dataB = ps.getDataV('C', nSamples, returnOverflow=False)
        dataC = ps.getDataV('D', nSamples, returnOverflow=False)

        j = {'A': list(dataA), 'B': list(dataB), 'C': list(dataC)}
        fout.write(json.dumps(j) + '\n')
        fout.flush()
        loopi += 1

    ps.stop()
    ps.close()

    # Uncomment following for call to .show() to not block
    # plt.ion()

    if 0:
        dataTimeAxis = np.arange(nSamples) * actualSamplingInterval
    
        plt.figure()
        plt.hold(True)
        plt.plot(dataTimeAxis, dataA, label="Power")
        plt.plot(dataTimeAxis, dataC, label="Clock")
        plt.grid(True, which='major')
        plt.title("Picoscope 6000 waveforms")
        plt.ylabel("Voltage (V)")
        plt.xlabel("Time (ms)")
        plt.legend()
        plt.show()
