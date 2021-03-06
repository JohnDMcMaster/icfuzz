#!/usr/bin/env python

import argparse
from PIL import Image
import numpy as np
import json
import base64
import binascii

# http://www.janeriksolem.net/2009/06/histogram-equalization-with-python-and.html
#def histeq(buff, nbr_bins=0x10000):
def histeq(buff, nbr_bins=0x100):
    im = np.array(buff)

    #get image histogram
    imhist, bins = np.histogram(im.flatten(), nbr_bins,normed=True)
    cdf = imhist.cumsum() #cumulative distribution function
    #cdf = (nbr_bins - 1) * cdf / cdf[-1] #normalize
    cdf = 255 * cdf / cdf[-1] #normalize
    #print cdf[0:10]
    
    #use linear interpolation of cdf to find new pixel values
    im2 = np.interp(im.flatten(), bins[:-1], cdf)
    rs = im2.reshape(im.shape)
    
    return rs

def scale(buff):
    low = min(buff)
    high = max(buff)
    print('Lo: %0.6f' % low)
    print('Hi: %0.6f' % high)
    for i in range(len(buff)):
        buff[i] = 255. * (buff[i] - low) / (high - low)

#(r, g, b)
status2c = {
    # While
    'secure': (255, 255, 255),
    # Red
    'overcurrent': (255, 0, 0),
    'overcurrent': (255, 0, 0),
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Post process fuzzing')
    parser.add_argument('fin', help='Input log file')
    parser.add_argument('ref_fin', help='Input bin file')
    args = parser.parse_args()

    print('Loading...')
    jlf = open(args.fin, 'r')
    ref = open(args.ref_fin, 'rb').read()

    metaj = json.loads(jlf.readline())

    cols = metaj['cols']
    rows = metaj['rows']
    print('Size: %dc x %dr' % (cols, rows))
    print('Plotting...')
    im = Image.new("RGB", (cols, rows), "white")
    nlines = 0
    allzeros = 0
    allones = 0
    matches = 0
    others = 0
    baselines = 0
    baseline = None
    exceptions = 0
    sampn = 1
    freqs = {}
    done = False
    for row in range(rows):
        if done:
            break
        for col in range(cols):
            if done:
                break
            for samplei in range(sampn):
                line = jlf.readline()
                if not line:
                    print("WARNING: incomplete data")
                    done = True
                    break
                try:
                    j = json.loads(line)
                except:
                    print("BAD: %s" % line)
                    raise
                # {"devfg": {"config": {"secure": true, "user_id1": 16383, "user_id0": 16383, "user_id3": 16383, "user_id2": 16383, "conf_word": 3}, "code": "AAAAA...AAAAAAAAAAAA=", "data": "AA...AAAAAAAAAA="}, "dumpi": 1, "y": 0.0, "x": 0.0, "type": "sample", "col": 0, "row": 0}
                def decode(k):
                    data = j['devcfg'].get(k)
                    if data is None:
                        return None
                    return base64.b64decode(data)
            
                code, data, config = (None, None, None)
                if 'devcfg' in j:
                    code = decode('code')
                    data = decode('data')
                    # config = j['devcfg'].get('config', {})
 
                freqs[code] = freqs.get(code, 0) + 1
                c = (0, 0, 255)
                # Exception, namely overcurrent
                if 'e' in j:
                    e = j['e']
                    #print e
                    c = (255, 0, 0)
                    exceptions += 1
                # Shoud have this if no error
                elif code is not None:
                    # All 0's => protected
                    def allzero():
                        for c in code:
                            if c != '\x00':
                                return False
                        return True
                    def allone():
                        for c in code:
                            if c not in ('\xFF', '\x3F'):
                                return False
                        return True
                    def ismatch():
                        # Most of the time this is due to metadata in bp format
                        ref2 = ref[0:len(code)]
                        if len(ref2) != len(code):
                            raise Exception("Bad reference w/ ref size %d, got %d" % (len(ref), len(code)))
                        for refc, readc in zip(ref2, code):
                            if refc != readc:
                                return False
                        return True

                    if baseline is None:
                        baseline = code

                    if ismatch():
                        matches += 1
                        # green
                        c = (0, 255, 0)
                    elif allzero():
                        allzeros += 1
                        # black
                        c = (0, 0, 0)
                    elif allone():
                        allones += 1
                        # white
                        c = (255, 255, 255)
                    elif code == baseline:
                        baselines += 1
                        # gray
                        c = (127, 127, 127)
                    # Some other state
                    else:
                        others += 1
                        # blue
                        c = (0, 0, 255)
                else:
                    print(j)
                    raise Exception('No code, no exception')
                    #c = (16, 16, 16)

                im.putpixel((col, row), c)
                nlines += 1
    
    print('Have %d / %d points' % (nlines, rows * cols * 3))
    print('  All 0:       %d' % allzeros)
    print('  All 1:       %d' % allones)
    print('  Matches:     %d' % matches)
    print('  Baseline:    %d' % baselines)
    print('  Others:      %d' % others)
    print('  Exceptions:  %d' % exceptions)

    print('Raw frequency dist')
    for code, freq in sorted(list(freqs.items()), key=lambda x: (x[1], x[0])):
        if code is None:
            s = 'None'
        else:
            s = binascii.hexlify(code[0:16])
        print('  %d w/ %s' % (freq, s))

    fnout = args.fin.replace('.jl', '.png')
    if fnout == args.fin:
        raise Exception('Expecting .jl file')
    print('Saving to %s...' % fnout)
    im.save(fnout)

    fnout = args.fin.replace('.jl', '_big.png')
    im.resize((im.size[0] * 8, im.size[1] * 8)).save(fnout)

    print('Done')

