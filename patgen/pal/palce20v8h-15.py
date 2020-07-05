#!/usr/bin/env python3
import struct
import random

SZ = 0x153

f = open('palce20v8h-15_c16_%05u_0x%04X.bin' % (SZ, SZ), 'wb')
for i in range(0, SZ, 2):
    f.write(struct.pack('>H', i))


buff = bytearray()
for i in range(0, SZ):
    buff += struct.pack('>B', random.randint(0, 255))
open('palce20v8h-15_rnd_%04x.bin' % (struct.unpack(">I", buff[0:4]))[0], 'wb').write(buff)

