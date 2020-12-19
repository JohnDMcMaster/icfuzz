import argparse
import csv
import matplotlib.pyplot as plt
import sys
from scipy import stats
import numpy as np
import json
from scipy.stats import pearsonr

def loadf(fn):
    ret = []
    for l in open(fn, 'r'):
        j = json.loads(l)
        ret.append(j['A'])
    return ret

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot')
    parser.add_argument('fin1',  help='Input csv')
    parser.add_argument('fin2',  help='Input csv')
    args = parser.parse_args()

    print 'Loading...'
    dat1 = loadf(args.fin1)
    dat2 = loadf(args.fin2)
    print('Correlating')
    pearsons = []
    # both trace sets should be the same length capture
    assert len(dat1[0]) == len(dat2[0])
    for ti in xrange(len(dat1[0])):
        print(ti)
        pxs = []
        pys = []
        for tracei in xrange(len(dat1)):
            pxs.append(dat1[tracei][ti])
            pys.append(0)
        for tracei in xrange(len(dat2)):
            pxs.append(dat2[tracei][ti])
            pys.append(1)
        pc, pval = pearsonr(pxs, pys)
        pearsons.append(pc)

    plt.plot(pearsons)
    if 0:
        plt.savefig('out.png')
    else:
        plt.show()
