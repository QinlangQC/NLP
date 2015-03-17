"""
    Viterbi algorithm dealing with low-frequent words
"""
import sys
import count_freqs
import viterbi

def replace_low_frequent(input_file, output_file): # Replace low frequent words in the input file with special labels
    input = open(input_file, 'r')
    lines = input.readlines()
    new_lines = []
    flag = False
    for line in lines:
        line = line.rstrip()
        words = line.split(' ')
        word = words[0]
        if word.isalpha() and word.isupper():
            if word.find('.') != -1:
                word = '_CAP_DOT_'
            else: word = '_CAP_'
        if word.replace(',', '').isdigit(): # Check if the word contains only numerals
            word = '_DIGIT_'

        # if len(word) > 0 and word[0].isupper() and word[1:].islower() and flag:
        #     word = '_initCAP_'
        # if not flag:
        #     word = '_firstWord_'
        #flag = True
        #if line == '':
            #flag = False
        words[0] = word
        line = ' '.join(words)
        new_lines.append(line)
        out = open(output_file, 'w')
    for line in new_lines:
        out.write('%s\n' % line)
    input.close()
    out.close()

def count_frequency(input, out_file):
    input = open(input, 'r')
    out_file = open(out_file, 'w')
    # Initialize a trigram counter
    counter = count_freqs.Hmm(3)
    # Collect counts
    counter.train(input)
    # Write the counts
    counter.write_counts(out_file)
    input.close()
    out_file.close()

def find_rare(file):
    input = open(file, 'r')
    words_dict = {}
    rare_words = {}
    lines = input.readlines()
    for line in lines:
        if line.find('WORDTAG') == -1:
            continue
        words_in_lines = line.split(' ')
        words_in_lines[3] = words_in_lines[3].rstrip()
        if words_in_lines[3] in words_dict:
            words_dict[words_in_lines[3]] += int(words_in_lines[0])
        else:
            words_dict[words_in_lines[3]] = int(words_in_lines[0])
    for key in words_dict:
        if words_dict[key] < 5:
            rare_words[key] = True
    input.close()
    return rare_words

def replece_rare(rare_words, input_file):
    input = open(input_file, 'r')
    new_tags = []
    lines = input.readlines()
    for line in lines:
        words = line.split(' ')
        if words[0] in rare_words:
            line = "_RARE_ " + words[1]
        new_tags.append(line)
    input.close()
    return new_tags

def output_new_train(new_tags, out_file):
    out = open(out_file, 'w')
    for item in new_tags:
        out.write("%s" % item)
    out.close()

def viterbi_sentences(vars, outfile, org_test_file):
    org_test = open(org_test_file)
    lines = org_test.readlines()
    org_sentences = []
    sentence = []
    for line in lines:
        line = line.rstrip()
        if line != '':
            sentence.append(line)
        else:
            org_sentences.append(sentence)
            sentence = []
    for x in range(len(vars.sentences)):
        y, pi = viterbi.viterbi(vars, vars.sentences[x])
        outfile.write('%s %s %f\n' % (org_sentences[x][0], y[0], pi[1]['* ' + str(y[0])]))
        for i in range(1,len(vars.sentences[x])):
            outfile.write('%s %s %f\n' % (org_sentences[x][i], y[i], pi[i + 1][y[i-1] + ' ' + y[i]]))
        outfile.write('\n')

def usage():
    print """
        python low_freq_viterbi.py [train_data] [test_data] > low_freq.prediction
    """

def main():
    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    replace_low_frequent(sys.argv[1], './low_freq_ner_train.dat')
    replace_low_frequent(sys.argv[2], './low_freq_ner_dev.dat')


    # Count the frequencies of the training file been replaced
    count_frequency('./low_freq_ner_train.dat', './ner.counts')

    # Find rare words and replace them with rare label
    rare_words = find_rare('./ner.counts')
    new_tags = replece_rare(rare_words, './low_freq_ner_train.dat')
    output_new_train(new_tags, './low_freq_ner_train.dat')

    # Recalculate frequency
    count_frequency('./low_freq_ner_train.dat', './low_freq_ner.counts')

    # Use the Viterbi algorithm
    vars = viterbi.Varibles('./low_freq_ner.counts', './low_freq_ner_dev.dat')
    viterbi_sentences(vars, sys.stdout, sys.argv[2])

if __name__ == "__main__":
    main()

