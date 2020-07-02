import struct

# to 32 KB
for sz in range(0, 16): 
    SZ = 1 << sz
    f = open('c16_%05u_0x%04X.bin' % (SZ, SZ), 'w')

    for i in xrange(0, SZ, 2):
        f.write(struct.pack('>H', i))

