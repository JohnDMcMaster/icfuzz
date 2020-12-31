#!/usr/bin/env python3

'''
Erase until the chip reports erased stable for 10% of the lead up time

https://www.electronicspoint.com/forums/threads/can-uv-leds-erase-eproms.25584/
"An old Intel appnote suggested that the UV dose required for reliable
erasure is five times the dose required to erase all the bits."
Maybe that's a good starting point for reliable erase
But let's do shorter for min erase right now
'''

from proghal import progs
from proghal.util import tostr, default_date_dir, mkdir_p

import json
import datetime
import time
import zlib
import binascii
import hashlib

def popcount(x):
    return bin(x).count("1")

def is_erased1(fw, prog_dev):
    # for now assume all 1's is erased
    # on some devices like PIC this isn't true due to file 0 padding
    percent = 100.0 * sum(bytearray(fw)) / (len(fw) * 0xFF)
    return percent == 100.0, percent

def is_erased(fw, prog_dev):
    # for now assume all 1's is erased
    # on some devices like PIC this isn't true due to file 0 padding
    percent = 100.0 * sum([popcount(x) for x in bytearray(fw)]) / (len(fw) * 8)
    return percent == 100.0, percent

def hash8(buf):
    return tostr(binascii.hexlify(hashlib.md5(buf).digest())[0:8])

def read_fw(prog, args):
    devcfg = None
    e = None
    # Try a few times to get a valid read
    try:
        cfg = {}
        progs.apply_run_args(args, cfg, "read")
        devcfg = prog.read(cfg)
        return devcfg, None
    except Exception as e:
        # Sometimes still get weird errors
        print('WARNING: unknown error: %s' % str(e))
        return None, e

def fw2str(fw):
    return tostr(binascii.hexlify(zlib.compress(fw)))

def run(fnout, prog_dev, args, ethresh=20., interval=3.0):
    print("")
    print('Initializing programmer')
    init_cfg = {}
    progs.apply_init_args(args, init_cfg)
    prog = progs.get_prog(args.prog_prog, init_cfg)
    print('Programmer ready')

    with open(fnout, 'w') as fout:
        j = {'type': 'header', 'prog_dev': prog_dev, 'date': datetime.datetime.utcnow().isoformat(), 'interval': interval, 'ethresh': ethresh}
        fout.write(json.dumps(j) + '\n')

        tstart = time.time()
        tlast = None
        thalf = None
        passn = 0
        nerased = 0
        while True:
            if tlast is not None:
                while time.time() - tlast < interval:
                    time.sleep(0.1)
    
            tlast = time.time()
            now = datetime.datetime.utcnow().isoformat()
            passn += 1
            devcfg, e = read_fw(prog, args)
            assert e is None, str(e)
            fw = devcfg['code']
            erased, erase_percent = is_erased(fw, prog_dev)
            if erased:
                nerased += 1
            else:
                nerased = 0
            pcomplete = 100.0 * nerased / passn

            j = {'iter': passn, 'date': now, 'fw': fw2str(fw), 'pcomplete': pcomplete, 'erase_percent': erase_percent, 'erased': erased}
            fout.write(json.dumps(j) + '\n')

            signature = hash8(fw)
            print('%s iter %u: erased %u w/ erase_percent %0.3f%%, sig %s, erase completion: %0.1f' % (now, passn, erased, erase_percent, signature, 100. * pcomplete / ethresh))
            if thalf is None and erase_percent >= 50:
                thalf = tlast
                dt_half = thalf - tstart
                print('50%% erased after %0.1f sec' % (dt_half,))
            if pcomplete >= ethresh:
                break
        dt = tlast - tstart
        print('120%% erased after %0.1f sec' % (dt,))

        j = {'type': 'footer', 'etime': dt, 'half_etime': dt_half}
        fout.write(json.dumps(j) + '\n')
    return dt, dt_half

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')
    progs.add_args(parser, prefix="prog-")
    parser.add_argument('--postfix', default=None, help='')
    parser.add_argument('fout', nargs='?', help='')
    args = parser.parse_args()

    fout = args.fout
    if fout is None:
        fout = default_date_dir("out", "", args.postfix) + ".jl"
        print("Selected %s" % fout)
        mkdir_p("out")

    run(fout, args.prog_device, args)
