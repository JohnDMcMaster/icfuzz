#!/usr/bin/env python3
import struct

SZ = 0x153
f = open('palce20v8h-15_c16_%05u_0x%04X.bin' % (SZ, SZ), 'wb')

for i in range(0, SZ, 2):
    f.write(struct.pack('>H', i))

