#!/usr/bin/env python
import struct

# to 256 byte
for sz in range(0, 9): 
    SZ = 1 << sz
    f = open('c8_%05u_0x%04X.bin' % (SZ, SZ), 'w')

    for i in xrange(0, SZ):
        f.write(struct.pack('>B', i))

