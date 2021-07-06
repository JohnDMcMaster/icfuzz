#!/usr/bin/env python3

"""
PAL16R8A2NC
As photographed each word is a column
Column order is odd (obfuscated?)
Row order is consistent with other ROMs

Order determined by blowing fuses while observing ROM w/ IR camera
Then images were manually ordered

Die oriented with text right side up
"""


from main import make_jed
from zorrom import mrom
from zorrom.util import add_bool_arg, parser_grcs, parse_grcs

"""
Visually ordered to be in physical order
a00_30w_01b.jpg
a01_30w_29b.jpg
a02_30w_00b.jpg
a03_30w_28b.jpg
a04_30w_03b.jpg
a05_30w_31b.jpg
a06_30w_02b.jpg
a07_30w_30b.jpg
a08_30w_05b.jpg
a09_30w_25b.jpg
a10_30w_04b.jpg
a11_30w_24b.jpg
a12_30w_07b.jpg
a13_30w_27b.jpg
a14_30w_06b.jpg
a15_30w_26b.jpg
a16_30w_09b.jpg
a17_30w_21b.jpg
a18_30w_08b.jpg
a19_30w_20b.jpg
a20_30w_11b.jpg
a21_30w_23b.jpg
a22_30w_10b.jpg
a23_30w_22b.jpg
a24_30w_13b.jpg
a25_30w_17b.jpg
a26_30w_12b.jpg
a27_30w_16b.jpg
a28_30w_15b.jpg
a29_30w_19b.jpg
a30_30w_14b.jpg
a31_30w_18b.jpg
"""
# Logical bit position to physical position within a column
# Physical index 0 at top
# Obfuscated?
bit_row2index = {
    0: 1,
    1: 29,
    2: 0,
    3: 28,
    4: 3,
    5: 31,
    6: 2,
    7: 30,
    8: 5,
    9: 25,
    10: 4,
    11: 24,
    12: 7,
    13: 27,
    14: 6,
    15: 26,
    16: 9,
    17: 21,
    18: 8,
    19: 20,
    20: 11,
    21: 23,
    22: 10,
    23: 22,
    24: 13,
    25: 17,
    26: 12,
    27: 16,
    28: 15,
    29: 19,
    30: 14,
    31: 18,
    }
bit_index2row = {}
for k, v in bit_row2index.items():
    bit_index2row[v] = k
assert len(bit_index2row) == 32

# Convert a word physical index to logical index
# Physical starting from left and counting up
# This table seems fairly straightforward
# and not too different than ROMs
# Some entries were missing and interpolated
word_col2log = [
    # 63-56
    63,
    62,
    61,
    60,
    59,
    58,
    57,
    56,
    # 48-55
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    # 47-40
    47,
    46,
    45,
    44,
    43,
    42,
    41,
    40,
    # 32-39
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    # 31-24
    31,
    30,
    29,
    28,
    27,
    26,
    25,
    24,
    # 16-23
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    # 15-8
    15,
    14,
    13,
    12,
    11,
    10,
    9,
    8,
    # 0-7
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    ]
assert len(word_col2log) == 64
word_col2log = dict(enumerate(word_col2log))

word_log2phys = {}
for k, v in word_col2log.items():
    word_log2phys[v] = k
assert len(word_log2phys) == 64

def munge_txt(txt,
              win,
              hin,
              rotate=None,
              flipx=False,
              flipy=False,
              invert=False):
    '''Return contents as char array of bits (ie string with no whitespace)'''
    assert rotate in (None, 0, 90, 180, 270)
    if rotate == 90 or rotate == 270:
        wout, hout = hin, win
    else:
        wout, hout = win, hin
    txtdict = mrom.txt2dict(txt, win, hin)
    if rotate not in (None, 0):
        txtdict = mrom.td_rotate(rotate, txtdict, wout, hout)
    if flipx:
        txtdict = mrom.td_flipx(txtdict, wout, hout)
    if flipy:
        txtdict = mrom.td_flipy(txtdict, wout, hout)
    if invert:
        txtdict = mrom.td_invert(txtdict, wout, hout)
    return txtdict, wout, hout

"""
Unufsed (bright) areas are 0 on bin
However bright areas are usually classified as 1
"""
def run(txt_in, jed_out, invert=True):
    txtin, win, hin = mrom.load_txt(open(txt_in, "r"), None, None)
    assert (win, hin) == (64, 32), (win, hin)
    
    if invert:
        txtin, win, hin = munge_txt(txtin, win, hin)

    words = [list("0" * 32) for _x in range(64)]
    for wordi in range(64):
        for biti in range(32):
            col = word_log2phys[wordi]
            row = bit_index2row[biti]
            words[wordi][biti] = txtin[(col, row)]
    jed = make_jed(words)
    open(jed_out, "w").write(jed)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('txt_in')
    parser.add_argument('jed_out', nargs='?')
    args = parser.parse_args()

    jed_out = args.jed_out
    if not jed_out:
        jed_out = args.txt_in.replace(".txt", ".jed")
        assert jed_out != args.txt_in

    run(txt_in=args.txt_in, jed_out=jed_out)
