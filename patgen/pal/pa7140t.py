#!/usr/bin/env python3
import struct
import random

SZ = 0xACB
prefix = "pa7140t"

f = open('%s_c16_%05u_0x%04X.bin' % (prefix, SZ, SZ), 'wb')

for i in range(0, SZ, 2):
    f.write(struct.pack('>H', i))


buff = bytearray()
for i in range(0, SZ):
    buff += struct.pack('>B', random.randint(0, 255))
firstword = struct.unpack(">I", buff[0:4])[0]
open('%s_rnd_%04x.bin' % (prefix, firstword), 'wb').write(buff)

