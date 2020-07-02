'''
AT89C51 firmware read power analysis torture test
'''

import struct

SZ = 4 * 1024
buff = bytearray('\x00' * SZ)

'''
Create recognizable transition + bit pattern
'''
# 32 bytes
pattern = \
    '\xFF\xFF\x00\x00' '\xFF\xFF\x00\x00' \
    '\xFF\xFF\x00\x00' '\xFF\xFF\x00\x00' \
    '\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00' \
    '\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00' \

open('at89c51_0.bin', 'w').write(buff)

for i in xrange(SZ):
    buff[i] = pattern[i % len(pattern)]

open('at89c51_pat2.bin', 'w').write(buff)

# invert
for i in xrange(SZ):
    buff[i] ^= 0xFF
open('at89c51_pat2i.bin', 'w').write(buff)

