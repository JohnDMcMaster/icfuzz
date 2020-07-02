import struct

'''
minipro -p 'PIC16C558 @DIP18' -c code -w pic16c558_cnt16s_minipro_data.bin
minipro -p 'PIC16C558 @DIP18' -c config -w pic16c558_cnt16s_minipro_fuses.conf
minipro -p 'PIC16C558 @DIP18' -r read.bin
cat fuses.conf
hexdump read.bin  |head
'''

prefix = 'pic16c558'
words = 2048
buff = bytearray('\xFF' * (words * 2))

def w14(addr, w):
    w1 = w & 0x3FFF
    if w1 != w:
        raise Exception("Data overflow")
    buff[addr:addr+2] = struct.pack('<H', w1)

def w16(addr, w):
    buff[addr:addr+2] = struct.pack('<H', w)

for i in xrange(words):
    w14(2 * i, i)

open('%s_cnt16s_minipro_data.bin' % (prefix,), 'w').write(buff)

fuses = '''user_id0 = 0x0100
user_id1 = 0x0102
user_id2 = 0x0104
user_id3 = 0x0106
conf_word = 0x3fbf'''
open('%s_cnt16s_minipro_fuses.conf' % (prefix,), 'w').write(fuses)

