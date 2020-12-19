import argparse
import csv
import matplotlib.pyplot as plt
import sys
from scipy import stats
import numpy as np

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot')
    parser.add_argument('fin',  help='Input csv')
    args = parser.parse_args()

    print 'Loading...'
    fin = args.fin
    crf = open(fin, 'r')
    crf.readline()
    crf.readline()
    

    seconds = []
    volts = []
    for l in crf:
        second, volt = l.split(',')
        seconds.append(float(second))
        volts.append(float(volt))

    div = 1
    seconds = [np.mean(seconds[i:i+div]) for i in xrange(0, len(seconds), div)]
    volts = [np.mean(volts[i:i+div]) for i in xrange(0, len(volts), div)]


    plt.plot(seconds, volts)
    fout = fin.replace('.CSV', '.png')
    assert fin != fout
    if 0:
        plt.savefig(fout)
    else:
        plt.show()
