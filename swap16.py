#!/usr/bin/env python3

import struct

def run(fnin, fnout):
    buf_in = open(fnin, "rb").read()
    buf_out = bytearray()
    assert len(buf_in) % 2 == 0
    for offset in range(0, len(buf_in), 2):
        word = buf_in[offset:offset+2]
        buf_out += word[1:2] + word[0:1]
    open(fnout, "wb").write(buf_out)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Swap endianess on 16 bit words')
    parser.add_argument('fin')
    parser.add_argument('fout')
    args = parser.parse_args()
    
    run(args.fin, args.fout)


if __name__ == "__main__":
    main()
