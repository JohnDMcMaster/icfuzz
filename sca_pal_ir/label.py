#!/usr/bin/env python3
from collections import OrderedDict
import re
import glob
import os
import shutil
import math
import json

sdir = "s3"

def load_json(fn, ret=None):
    # (word, bit) to  basename
    if ret is None:
        ret = {}
    for l in open(fn, "r"):
        # {"fn": "0241.jpg", "word": 0, "bit": 18}
        j = json.loads(l)
        ret[(j["word"], j["bit"])] = j["fn"]
    return ret

def label_json(fn):
    for (word, bit), basename in load_json(fn).items():
        shutil.copy(os.path.join(sdir, "img", basename), os.path.join(sdir, "labeled", "%02uw_%02ub.jpg" % (word, bit)))

def run():
    # s2
    if 0:
        # pos2fn = load_json("out1.json")
        label_json("out1.json")
        label_json("out2.json")
        label_json("out3.json")
        # out4_bad.json
        # no usable data?
        # out5_bad.json
        # has some blown fuses
    
        label_json("out6_interrupt.json")
        label_json("out7.json")

    # s3
    if 1:
        label_json("s3/out1_first2.json")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')
    args = parser.parse_args()

    run()
