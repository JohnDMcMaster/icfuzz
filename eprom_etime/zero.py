#!/usr/bin/env python3

from proghal import progs

import json
import datetime
import time
import zlib
import binascii
import hashlib

def read_fw(prog, args):
    cfg = {}
    progs.apply_run_args(args, cfg, "read")
    return prog.read(cfg)["code"]

def write_fw(prog, fw, args):
    cfg = {"code": fw}
    progs.apply_run_args(args, cfg, "write")
    return prog.write(cfg)

def run( prog_dev, args):
    print("")
    print('Initializing programmer')
    init_cfg = {}
    progs.apply_init_args(args, init_cfg)
    prog = progs.get_prog(args.prog_prog, init_cfg)
    print('Programmer ready')

    ref_fw = read_fw(prog, args)
    nbytes = len(ref_fw)
    print("Reference firmware: %u bytes" % nbytes)

    fw = bytearray(nbytes)
    write_fw(prog, fw, args)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Write all bits to 0 of given device')
    progs.add_args(parser, prefix="prog-")
    args = parser.parse_args()

    run(args.prog_device, args)
