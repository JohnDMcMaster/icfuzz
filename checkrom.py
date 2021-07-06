#!/usr/bin/env python3
"""
Run statistics checks on .bin file to look for common issues
In particular look for stuck address and/or bit lines
"""

import math

def check_bits_toggle(buff):
    """
    Verify all 8 bits toggle
    """
    ok = True
    # Ideally this would be per word
    bit_set = set()
    bit_clear = set()
    for biti in range(8):
        sets = 0
        clears = 0
        for b in buff:
            if b & (1 << biti):
                bit_set.add(biti)
                sets += 1
            else:
                bit_clear.add(biti)
                clears += 1
        print("bit %u sets %u, clears %u" % (biti, sets, clears))
    if len(bit_set) != 8:
        ok = False
    if len(bit_clear) != 8:
        ok = False
    print("Set bits: %u, cleared bits: %u, ok %s" % (len(bit_set), len(bit_clear), ok))
    return ok

def check_stuck_addr(buff):
    retok = True
    """
    Look for aliasing on address lines
    ie if an address bit is stuck
    """
    # assert len(buff) == 32768
    addrn = int(math.log(len(buff), 2))
    print("Address bits %u" % addrn)
    for addrbit in range(addrn):
        # Find at least one case where bits are not aliased
        addrmask = 1 << addrbit
        
        matches = 0
        mismatches = 0
        for addr in range(len(buff)):
            l = buff[addr]
            r = buff[addr ^ addrmask]
            if l != r:
                mismatches += 1
            else:
                matches += 1
        ok = mismatches > 0
        retok = retok & ok
        print("bit %u (0x%04X) ok %s" % (addrbit, addrmask, ok))
        print("  matches %u, mismatches %u" % (matches, mismatches))
    return retok

def run(fin):
    ok = True
    print("Reading %s" % fin)
    buff = open(fin, "rb").read()
    print("")
    ok = ok & check_bits_toggle(buff)
    print("")
    ok = ok & check_stuck_addr(buff)
    print("")
    print("Overall: %s" % (ok,))

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Verify ROM has no stuck bits')
    parser.add_argument('fin')
    args = parser.parse_args()
    
    run(args.fin)


if __name__ == "__main__":
    main()
