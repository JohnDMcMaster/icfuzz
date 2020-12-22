#!/usr/bin/env python3

'''
Scans across a die
Assumes laser pointer pointed at die not under active control
Also works for microscope shining (possibly with diaghragm mask)
Finds areas that changes chip operation
Dumbed down version of "ezfuzz"
'''

from uscope.hal.cnc import lcnc_ar
from uscope.benchmark import time_str

from bpwahk import BPWAHK

import argparse
import time
import datetime
import os
import json
import base64
import hashlib
import binascii

def read_fw(bp, cont):
    devcfg = None
    e = None
    # Try a few times to get a valid read
    try:
        devcfg = bp.read_bin()
        break
    except Exception as e:
        # Sometimes still get weird errors
        #raise
        print('WARNING: unknown error: %s' % str(e))
    return devcfg, e

def myhash(buff):
    return binascii.hexlify(hashlib.md5.new(buff).digest())

def hash8(myhash):
    return myhash[0:8] if myhash else 'None'

def do_run(hal, bp, width, height, dry, fout, xstep, ystep, samples=1, cont=True):
    # Use focus to adjust
    verbose = False
    x0 = 0.0
    y0 = 0.0
    if 0:
        x0 = 2.0
        y0 = 2.0

    backlash = 0.1
    hal.mv_abs({'x': x0 - backlash, 'y': y0 - backlash})

    jf = fout

    cols = int(width / xstep)
    rows = int(height / ystep)
    tstart = time.time()

    print('Dummy firmware read')
    trstart = time.time()
    devcfg, e = read_fw(bp, cont)
    if not devcfg:
        #raise Exception("Failed to get baseline!")
        print('WARNING: failed to get baseline!')
        base_code_hash = None
    else:
        base_code_hash = myhash(devcfg)
        print('Baseline: %s' % (hash8(base_code_hash),))
    trend = time.time()
    tread = trend - trstart
    print('Read time: %0.1f' % tread)

    # FIXME: estimate
    tmove = 0.1
    tsample = tread + tmove
    print('Sample time: %0.1f' % tsample)
    net_samples = cols * rows * samples
    print('Taking %dc x %dr x %ds => %d net samples => ETA %s' % (cols, rows, samples, net_samples, time_str(tsample * net_samples)))

    if jf:
        j = {
            'type': 'params',
            'x0': x0,
            'y0': y0,
            'xstep': xstep,
            'ystep': ystep,
            'cols': cols,
            'rows': rows,
            'samples': samples,
            'net_samples': net_samples,
        }
        jf.write(json.dumps(j) + '\n')
        jf.flush()

    posi = 0
    for row in range(rows):
        y = y0 + row * ystep
        hal.mv_abs({'x': x0 - backlash, 'y': y})
        for col in range(cols):
            posi += 1
            x = x0 + col * xstep
            hal.mv_abs({'x': x})
            print('%s taking %d / %d @ %dc, %dr (G0 X%0.1f Y%0.1f)' % (datetime.datetime.utcnow(), posi, nsamples, col, row, x, y))
            # Hit it a bunch of times in case we got unlucky
            for dumpi in range(samples):
                j = {
                    'type': 'sample',
                    'row': row, 'col': col,
                    'x': x, 'y': y,
                    'dumpi': dumpi,
                    }

                if dry:
                    devcfg, e = None, None
                else:
                    devcfg, e = read_fw(device, cont)

                if devcfg:
                    # Some crude monitoring
                    # Top histogram counts would be better though
                    code_md5 = myhash(devcfg)
                    print('  %d %s' % (dumpi, hash8(code_md5)))
                    if code_md5 != base_code_hash:
                        print('    code...: %s' % binascii.hexlify(devcfg['code'][0:16]))
                if e:
                    j['e'] = (str(type(e).__name__), str(e)),

                if jf:
                    jf.write(json.dumps(j) + '\n')
                    jf.flush()

    print('Ret home')
    hal.mv_abs({'x': x0, 'y': y0})
    print('Movement done')
    tend = time.time()
    print('Took %s' % time_str(tend - tstart))

def run(cnc_host, dry, width, height, fnout, step, samples=1, force=False):
    hal = None

    try:
        print("")
        print('Initializing LCNC')
        hal = lcnc_ar.LcncPyHalAr(host=cnc_host, dry=dry, log=None)

        print("")
        print('Initializing programmer')
        bp = BPWAHK()

        fout = None
        if not force and os.path.exists(fnout):
            raise Exception("Refusing to overwrite")
        if not dry:
            fout = open(fnout, 'w')

        print("")
        print('Running')
        do_run(hal=hal, bp=bp, width=width, height=height, dry=dry, fout=fout, xstep=step, ystep=step, samples=samples)
    finally:
        print('Shutting down hal')
        if hal:
            hal.ar_stop()

def main():
    parser = argparse.ArgumentParser(description='Use ezlaze to fuzz dice')
    parser.add_argument('--cnc', default='mk', help='LinuxCNC host')
    parser.add_argument('--dry', action='store_true', help='Dry run')
    parser.add_argument('--force', action='store_true', help='Overwrite file')
    parser.add_argument('--samples', type=int, default=1, help='Number of times to read each location')
    parser.add_argument('--width', type=float, default=1, help='X width (ie in mm)')
    parser.add_argument('--height', type=float, default=1, help='y height (ie in mm)')
    parser.add_argument('--step', type=float, default=1.0, help='Step size (ie in mm)')
    parser.add_argument('--device', help='IC device type)')
    parser.add_argument('fout', nargs='?', default='scan.jl', help='Store data to, 1 JSON per line')
    args = parser.parse_args()

    run(cnc_host=args.cnc, dry=args.dry, width=args.width, height=args.height, fnout=args.fout, step=args.step, samples=args.samples, force=args.force)

if __name__ == "__main__":
    main()
