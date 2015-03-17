
"""
    Implement CKY algorithm to parse sentences based on vertical markovization
"""
from math import *
import json, sys, time

class Parameters:
    "Store the parameters need"
    def __init__(self):
        self.xyz = {}
        self.xw = {}
        self.nonterminal = {}
        self.unary_rule = {}
        self.binary_rule = {}
        self.terminal = {}

    def calculate(self, count_file):
        for l in open(count_file):
            if l.find('NONTERMINAL') != -1:
                w = l.rstrip().split(' ')
                self.nonterminal[w[2]] = int(w[0])
            elif l.find('UNARYRULE') != -1:
                 w = l.rstrip().split(' ')
                 if w[2] not in self.unary_rule:
                     self.unary_rule[w[2]] = {}
                 self.unary_rule[w[2]][w[3]] = int(w[0])
                 if w[3] not in self.terminal:
                     self.terminal[w[3]] = 1
            else:
                w = l.rstrip().split(' ')
                t = (w[3], w[4])
                if w[2] not in self.binary_rule:
                    self.binary_rule[w[2]] = {}
                self.binary_rule[w[2]][t] = int(w[0])

        for x in self.binary_rule:
            for key in self.binary_rule[x]:
                self.xyz[(x, key[0], key[1])] = log(float(self.binary_rule[x][key]) / float(self.nonterminal[x]), 2)
        for x in self.unary_rule:
            for key in self.unary_rule[x]:
                self.xw[(x, key)] = log(float(self.unary_rule[x][key]) / float(self.nonterminal[x]), 2)

def CKY_initialize(words, parameters):
    "Initilize the two vectors"
    pi = {}
    bp = {}
    for i in range(len(words)):
        for j in range(i, len(words)):
            pi[(i, j)] = {}
            bp[(i, j)] = {}
            for key in parameters.nonterminal:
                pi[(i, j)][key] = float('-inf');
                bp[(i, j)][key] = ('none', -1)
                if i == j and key in parameters.unary_rule and words[i] in parameters.unary_rule[key]:
                    pi[(i, i)][key] = parameters.xw[(key, words[i])]
                    bp[(i, i)][key] = ((key, words[i]), 0)
    return pi, bp

class CKY_sentence():
    "Parse by sentence"
    def __init__(self, bp, words):
        self.bp = bp
        self.words = words
        self.r = ''

    def build_tree(self, start, end, x):
        self.r += '["' + x + '", '
        if start == end:
            self.r += '"' + self.words[start] + '"]'
            return
        t = self.bp[(start, end)][x]
        self.build_tree(start, t[1], t[0][1])
        self.r += ", "
        self.build_tree(t[1] + 1, end, t[0][2])
        self.r += ']'

    def out_tree(self, outfile):
        outfile.write('%s\n' % self.r)

def CKY(words, parameters):
    "Implementation of CKY algorithm"
    pi, bp = CKY_initialize(words, parameters)
    n = len(words)
    for l in range(1, n):
        for i in range(0, n - l):
            j = i + l
            for x in parameters.binary_rule:
                for rule in parameters.binary_rule[x]:
                    for s in range(i, j):
                        t = (x, rule[0], rule[1])
                        if pi[(i, j)][x] < parameters.xyz[t] + pi[(i, s)][rule[0]] + pi[(s + 1, j)][rule[1]]:
                            pi[(i, j)][x] = parameters.xyz[t] + pi[(i, s)][rule[0]] + pi[(s + 1, j)][rule[1]]
                            bp[(i, j)][x] = (t, s)
    return pi, bp

def out(pi, bp, words, outfile):
    "Output the resuslt"
    sentence = CKY_sentence(bp, words)
    q = float('-inf')
    for ss in pi[(0, len(words) - 1)]:
        if q <= pi[(0, len(words) - 1)][ss]:
            q = pi[(0, len(words) - 1)][ss]
            x = ss
    if pi[(0, len(words) - 1)]['S'] != float('-inf') or q == float('-inf'):
        sentence.build_tree(0, len(words) - 1, 'S')
    else:
        sentence.build_tree(0, len(words) - 1, x)
    sentence.out_tree(outfile)

def usage():
    sys.stderr.write("""
    Usage: python CKY_vert.py [count_file] [test_file] [prediction_file]
        \n""")

def main():
    starttime=time.time()
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)
    parameters = Parameters()
    parameters.calculate(sys.argv[1])
    outfile = open(sys.argv[3], 'w')
    for l in open(sys.argv[2]):
        words = l.rstrip().split(' ')
        org_words = []
        for x in range(len(words)):
            org_words.append(words[x])
            if words[x] not in parameters.terminal:
                words[x] = '_RARE_'
        pi, bp = CKY(words, parameters)
        out(pi, bp, org_words, outfile)
    outfile.close()

    endtime=time.time()

    sys.stderr.write("Estimated time for viterbi:" + str((endtime-starttime)/60)+"\n")

if __name__ == "__main__":
    main()
