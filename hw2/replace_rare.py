"""
    Replace low frequent words (count(n) < 5) to '_RARE_' from file
"""

import json, sys
from count_cfg_freq import *

def replace_terminal(r, terminals):
    """
    Replace the infrequent words in a parse tree with rare
    :param r:
    :param terminals:
    :return:
    """
    if len(r) == 3:
        for i in range(1, 3):
            replace_terminal(r[i], terminals)
    if len(r) == 2:
        if terminals[r[1]] < 5:
            r[1] = '_RARE_'
    return r

def count_terminal(count_file):
    """
    Count the frequency of words in the file
    :param count_file:
    :return:
    """
    terminals = {}
    for line in open(count_file):
        if line.find('UNARYRULE') == -1:
            continue
        w = line.rstrip().split(' ')
        if w[3] in terminals:
            terminals[w[3]] += int(w[0])
        else:
            terminals[w[3]] = int(w[0])
    return terminals

def usage():
    sys.stderr.write("""
    Usage: python replace_rare.py [tree_file] [count_file] [out_file]
        \n""")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)
    terminals = count_terminal(sys.argv[2])
    outfile = open(sys.argv[3], 'w')
    for l in open(sys.argv[1]):
        record = json.loads(l)
        r = replace_terminal(record, terminals)
        json.dump(r, outfile)
        outfile.write('\n')


