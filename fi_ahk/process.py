#!/usr/bin/env python3
from collections import OrderedDict
import re
import glob
from PIL import Image
import os
import shutil
import math

nbits = None
imw = None
imh = None
imbits = None

def init_part(jed):
    global nbits
    global imw
    global imh
    global imbits
    
    part = jed["part"]
    nbits = jed["len"]
    if part == "PALCE20V8H-15":
        # these seem to map to actual layout
        imw = 66
        imh = 41

        imw = 40
        imh = 68
    elif part == "PA7140":
        # these should be close but aren't necessarily equal
        # imbits must be >= though
        assert nbits == 22103
        imw = 149
        imh = 149
    else:
        print("WARNING: unsupported part %s" % part)
        # round up square
        imw = imh = math.ceil(nbits**0.5) ** 2

    imbits = imw * imh
    print("Part %s w/ %u bits as %uw x %uh" % (part, nbits, imw, imh))
    assert imbits >= nbits, (imbits, nbits)

def load_jed(fn):
    """
    JEDEC file generated by 1410/84 from PALCE20V8H-15 06/28/20 22:42:11*
    DM AMD*
    DD PALCE20V8H-15*
    QF2706*
    G0*
    F0*
    L00000 0000000000000000000000000100000000000000*
    """
    ret = {}
    d = OrderedDict()
    with open(fn) as f:
        for l in f:
            # remove *, newline
            l = l.strip()[0:-1]
            if not l:
                continue
            parts = l.split(" ")
            if parts[0] == "DM":
                ret["vendor"] = parts[1]
            elif parts[0] == "DD":
                ret["part"] = parts[1]
            elif l[0:2] == "QF":
                ret["len"] = int(l[2:])
            elif l[0] == "L":
                # L00000 0000000000000000000000000100000000000000*
                addr, bits = l.split(" ")
                addr = int(addr[1:], 16)
                d[addr] = bits
            else:
                continue

    ret["data"] = d
    return ret

def jed2txt(jed):
    ret = ""
    for v in jed["data"].values():
        ret += v
    assert jed["len"] == nbits
    assert nbits == len(ret), (nbits, len(ret))
    return ret

def load_jed_flat(fn):
    jed = load_jed(fn)
    return jed2txt(jed)

"""
def gen_jeds(jed_run_dir):
    fns = sorted(glob.glob("%s/*.jed" % jed_run_dir))
    progress = len(fns) // 20
    for fni, fn in enumerate(fns):
        yield (fn, load_jed_flat(fn))
        if fni % progress == 0:
            print("%0.1f %%" % (100.0 * (fni + 1) / len(fns)))
"""

def load_log(fn):
    """
    ok
    <WINTXT></WINTXT>


    <WINTXT>OK
    Failed to perform operation on device.
    Invalid electronic signature in chip (algorithm ID).
    
    </WINTXT>
    """
    f = open(fn, "r")
    stat = f.readline().strip()
    txtbox = f.read()
    txtbox = txtbox.replace("<WINTXT>", "").replace("</WINTXT>", "")
    txtbox = txtbox.strip()
    return stat, txtbox


def txtbox2status(txtbox):
    if txtbox == "":
        assert 0
        return "ok"
    elif "Invalid electronic signature in chip " in txtbox:
        return "invalid_sig"
    elif "Save &File As" in txtbox or "&Help" in txtbox:
        return "ahk"
    elif "backwards" in txtbox:
        return "backwards"
    elif "Excessive current" in txtbox:
        return "overcurrent"
    else:
        assert 0, txtbox
        return "unknown"

def parse_dir(jed_run_dir):
    """
    return fn_id, status, jedtxt
    """

    #print(jed_run_dir)
    # while .jed file names can glitch if gui scripting goes off the rails, .log is reliable
    fns = sorted(glob.glob("%s/*.log" % jed_run_dir))
    progress = len(fns) // 20
    for fni, log_fn in enumerate(fns):
        if fni and fni % progress == 0:
            print("%0.1f %%" % (100.0 * (fni + 1) / len(fns)))
        stat, txtbox = load_log(log_fn)
        fn_id = os.path.basename(log_fn.replace(".log", ""))
        if stat != "ok":
            #print(stat, txtbox)
            # TODO: convert txtbox to error codes
            yield fn_id, txtbox2status(txtbox), None
            continue
        jed_fn = log_fn.replace(".log", ".jed")
        if not os.path.exists(jed_fn):
            yield fn_id, "missing", None
            continue
        yield fn_id, "ok", load_jed_flat(jed_fn)


    """
    #print(fn)
    # 3666_2020-07-01_22.16.14.jed
    # 2020-07-01_19.29.51.jed
    basename = os.path.basename(fn)
    if len(basename) != len("3666_2020-07-01_22.16.14.jed"):
        print("WARNING: skip bad fn %s" % fn)
        continue

last_jed = None
    if this_jed != last_jed:
        yield basename, this_jed
    last_jed = this_jed
    jed = load_jed_flat(jed_fn)
    """


def str2im(status, jed, refjed, protjed):
    """
    Goals:
    -Highlight correct values
    -Downplay values that happen to be correct in reference
    """
    # print(len(jedstr))
    im = Image.new("RGB", (imw, imh))
    i = 0
    for y in range(imh):
        for x in range(imw):
            if i >= nbits:
                break
            if status == "ok":
                if jed[i] == protjed[i]:
                    c = (128, 128, 128)
                elif jed[i] == refjed[i]:
                    # Constant 1
                    if jed[i] == "1":
                        c = (0, 192, 0)
                    # Constant 0
                    else:
                        c = (0, 128, 0)
                else:
                    if jed[i] == protjed[i]:
                        c = (128, 128, 128)
                    # 0 => 1
                    elif jed[i] == "1":
                        c = (255, 0, 0)
                    # 1 => 0
                    else:
                        c = (192, 0, 0)
            elif status == "invalid_sig":
                c = (0, 0, 64)
            elif status == "backwards":
                c = (0, 0, 128)
            elif status == "overcurrent":
                c = (128, 128, 0)
            elif status == "missing" or status == "ahk":
                c = (0, 0, 255)
            else:
                assert 0, status
            im.putpixel((x, y), c)
            i += 1
    return im.resize((imw * 8, imh * 8), resample=Image.NEAREST)

def mkscore(ref_jedtxt, jedtxt):
    if jedtxt is None:
        return 0
    return sum([x == y for x, y in zip(ref_jedtxt, jedtxt)])

def run(dir_fn):
    out_dir = os.path.join(dir_fn, "out")
    jed_run_dir = os.path.join(dir_fn, "ahk")
    # jl_fn = glob.glob(dir_fn + "/*.jl'")[0]

    ref_jed = load_jed(os.path.join(dir_fn, "ref.jed"))
    init_part(ref_jed)
    ref_jedtxt = jed2txt(ref_jed)
    prot_jedtxt = load_jed_flat(os.path.join(dir_fn, "prot.jed"))

    stats = {}
    scores = {}
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    data_diffs = 0
    any_diffs = 0
    for fn_id, status, jedtxt in parse_dir(jed_run_dir):
        if jedtxt == ref_jedtxt:
            print("Match %s" % fn_id)
        
        stats[status] = stats.get(status, 0) + 1
        scores[fn_id] = mkscore(ref_jedtxt, jedtxt)
        im = str2im(status, jedtxt, ref_jedtxt, prot_jedtxt)
        if jedtxt != prot_jedtxt:
            any_diffs += 1
        if status == "ok" and jedtxt != prot_jedtxt:
            im.save("%s/%s.png" % (out_dir, fn_id))
            data_diffs += 1
    

    scoresort = list(scores.items())
    scoresort.sort(key=lambda x: x[1], reverse=True)
    print("Top matches out of %u" % nbits)
    for rank, (fn_id, score) in enumerate(scoresort):
        if rank >= 5:
            break
        print("  %s: %u (%0.1f %%)" % (fn_id, score, 100.0 * score / nbits))

    print("Status distribution (%u net)" % sum(stats.values()))
    for k, v in sorted(stats.items()):
        print("  %s: %s" % (k, v))
    print("Not reference: %u" % any_diffs)
    print("Not reference and ok: %u" % data_diffs)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('dir', default=None, help='Dir of data vs time')
    args = parser.parse_args()

    run(args.dir)