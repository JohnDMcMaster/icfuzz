#!/usr/bin/python3

import sys

b = open(sys.argv[1], 'rb').read()

print('module pal16r8(clk, i, o);')
print('\tinput  clk;')
print('\tinput  [7:0] i; // pin  2 = i[0], pin  9 = i[7]')
print('\toutput [7:0] o; // pin 19 = o[0], pin 12 = o[7]')
print('\talways @(posedge clk) begin')
for line in range(8):
    base = 32 * (7 - line)
    s = ''
    for subline in range(8):
        keys = b[base + 4*subline:base + 4*subline + 4]
        if keys != b'\xff\xff\xff\xff':
            t = ''
            for i in range(8):
                if ((keys[i >> 1] >> (4*(i & 1))) & 1) == 0:
                    if t != '':
                        t += ' & '
                    t += 'i[%d]' % i
                if ((keys[i >> 1] >> (4*(i & 1)) + 1) & 1) == 0:
                    if t != '':
                        t += ' & '
                    t += '~i[%d]' % i
                if ((keys[i >> 1] >> (4*(i & 1)) + 2) & 1) == 0:
                    if t != '':
                        t += ' & '
                    t += 'o[%d]' % i
                if ((keys[i >> 1] >> (4*(i & 1)) + 3) & 1) == 0:
                    if t != '':
                        t += ' & '
                    t += '~o[%d]' % i
            if s != '':
                s += ' + '
            if '+' in t:
                t = '(' + t + ')'
            s += t
    if s == '':
        s = '\'1'
    else:
        s = '~(' + s + ')'
    print('\t\to[%d] <= %s;' % (line, s))
print('\tend')
print('endmodule')
