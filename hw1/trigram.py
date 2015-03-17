'''
    Compute the trigram log probability from the counts of trigrams
'''

import sys
from math import *

class Varables: # Store the intermediate vectors
    def __init__(self):
        self.count_uv = {}
        self.count_uvw = {}
        self.uvw_uv = {}
        self.trigram_prob = {}

def comput_count_uv(input): # Count the 2-gram
    count_uv = {}
    for line in input:
        if line.find('2-GRAM') == -1:
            continue
        line = line.rstrip()
        words = line.split(' ')
        uv = words[2] + ' ' + words[3]
        count_uv[uv] = int(words[0])
    return count_uv

def compute_count_uvw(input): # Count the 3-gram
    count_uvw = {}
    uvw_uv = {}
    for line in input:
        if line.find('3-GRAM') == -1:
            continue
        line = line.rstrip()
        words = line.split(' ')
        uv = words[2] + ' ' + words[3]
        uvw = uv + ' ' + words[4]
        uvw_uv[uvw] = uv
        count_uvw[uvw] = int(words[0])
    return count_uvw, uvw_uv

def compute_trigram_prob(file): # Compute the trigram probability
    trigram_prob = {}
    input = open(file, 'r')
    lines = input.readlines()
    count_uv = comput_count_uv(lines)
    count_uvw, uvw_uv= compute_count_uvw(lines)
    for key in count_uvw:
        trigram_prob[key] = log(count_uvw[key], 2) - log(count_uv[uvw_uv[key]], 2)
    input.close()
    return trigram_prob

def output(out_file, trigram):
    for key in trigram:
        out_file.write('%s %f\n' % (key, trigram[key]))

def usage():
    print """
    python trigram.py [train_counts] > [out_file]
    """

def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(2)

    trigram = compute_trigram_prob(sys.argv[1])
    output(sys.stdout, trigram)

if __name__ == "__main__":
   main()