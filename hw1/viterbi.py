'''
    Implement the Viterbi algorithm based on HMM
'''

import sys
from tagger import emission
from trigram import compute_trigram_prob
import time

class Varibles: # Store intermediate vectors
    def __init__(self, count_file, test_file):
        self.emission_prob = {}
        self.trigram_prob = {}
        self.x_yx = {}
        self.yx_y = {}
        self.uvw_uv = {}
        self.tags = []
        test = open(test_file, 'r')
        self.read_sentences(test)
        count = open(count_file, 'r')
        lines = count.readlines()
        for line in lines:
            if line.find('1-GRAM') == -1:
                continue
            w = line.rstrip().split(' ')
            self.tags.append(w[2])
        self.compute_trigram_prob(count_file)
        self.compute_emission_prob(count_file)

    def compute_emission_prob(self, file):
        self.emission_prob, self.x_yx, self.yx_y = emission(file)
        for x in self.x_yx:
            for tag in self.tags:
                wx = tag + ' ' + x
                if wx not in self.emission_prob:
                    self.emission_prob[wx] = float('-inf')

    def compute_trigram_prob(self, file):
        self.trigram_prob = compute_trigram_prob(file)
        for tag_a in self.tags:
            for tag_b in self.tags:
                for tac_c in self.tags:
                    abc = tag_a + ' ' + tag_b + ' ' + tac_c
                    if abc not in self.trigram_prob:
                        self.trigram_prob[abc] = float('-inf')

    def read_sentences(self, test):
        lines = test.readlines()
        self.sentences = []
        sentence = []
        for line in lines:
            line = line.rstrip()
            if line != '':
                sentence.append(line)
            else:
                self.sentences.append(sentence)
                sentence = []


def initilize(vars, sentence): # Initialize the two vectors in the Viterbi algorithm
    n = len(sentence)
    pi = {}
    bp = {}
    for k in range(0, n + 1):
        pi[k] = {}
        bp[k] = {}

    pi[0]['* *'] = 0
    for k in range(1, n + 1):
        for v in vars.tags:
            for w in vars.tags:
                vw = v + ' ' + w
                pi[k][vw] = float('-inf')
    return pi, bp

def viterbi(vars, sentence): # Implement the Viterbi algorithm
    n = len(sentence)
    pi, bp = initilize(vars, sentence)
    for w in vars.tags:
        uvw = '* * ' + w
        vw = '* ' + w
        x = sentence[0]
        if x not in vars.x_yx:
            x = '_RARE_'
        wx = w + ' ' + x
        if uvw in vars.trigram_prob:
            trans=vars.trigram_prob[uvw]
        else:
            trans=float('-inf')
        pi[1][vw] = trans + vars.emission_prob[wx]

    if n>1:
        for w in vars.tags:
            for v in vars.tags:
                uvw = '* '+ v + ' '+ w
                vw = v+' ' + w
                uv='* '+ v
                x = sentence[1]
                if x not in vars.x_yx:
                    x = '_RARE_'
                wx = w + ' ' + x
                if uvw in vars.trigram_prob:
                    trans=vars.trigram_prob[uvw]
                else:
                    trans=float('-inf')
                if pi[1][uv]+trans + vars.emission_prob[wx] >= pi[2][vw]:
                    pi[2][vw] = pi[1][uv]+trans + vars.emission_prob[wx]

    for k in range(3, n+1):
        for v in vars.tags:
            for w in vars.tags:
                for u in vars.tags:
                    vw = v + ' ' + w
                    x = sentence[k - 1]
                    if x not in vars.x_yx:
                        x = '_RARE_'
                    wx = w + ' ' + x
                    uv = u + ' ' + v
                    uvw = uv + ' ' + w
                    if pi[k - 1][uv] + vars.trigram_prob[uvw] + vars.emission_prob[wx] >= pi[k][vw]:
                        pi[k][vw] = pi[k - 1][uv] + vars.trigram_prob[uvw] + vars.emission_prob[wx]
                        bp[k][vw] = u

    y = [None] * n
    max = float('-inf')
    for v in vars.tags:
        for w in vars.tags:
            vw = v + ' ' + w
            vw_stop = vw + ' ' + 'STOP'
            if vw_stop in vars.trigram_prob:
                if pi[n][vw] + vars.trigram_prob[vw_stop] >= max:
                    y[n - 1] = w
                    y[n - 2] = v
                    max = pi[n][vw] + vars.trigram_prob[vw_stop]
    for k in range(1, n-1)[::-1]:
        vw = y[k] + ' ' + y[k + 1]
        y[k - 1] = bp[k + 2][vw]
    return y, pi

def viterbi_sentences(vars, outfile):
    for sentence in vars.sentences:
        y, pi = viterbi(vars, sentence)
        outfile.write('%s %s %f\n' % (sentence[0], y[0], pi[1]['* ' + str(y[0])]))
        for x in range(1,len(sentence)):
            outfile.write('%s %s %f\n' % (sentence[x], y[x], pi[x + 1][y[x-1] + ' ' + y[x]]))
        outfile.write('\n')

def usage():
    print """
    python viterbi.py [train_count] [test_data] > [prediction_file]
    """

def main():
    starttime=time.time()
    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    vars = Varibles(sys.argv[1], sys.argv[2])
    viterbi_sentences(vars, sys.stdout)

    endtime=time.time()

    sys.stderr.write("Estimated time for viterbi:" + str((endtime-starttime)/60)+"\n")

if __name__ == "__main__":
    main()