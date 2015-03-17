"""
    Count word_tag frequency taken into consideration rare words for question 4 in homework 1
"""

from count_freqs import *

def count_frequency(input, out_file):
    input = open(input, 'r')
    out_file = open(out_file, 'w')
    # Initialize a trigram counter
    counter = Hmm(3)
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

def output_new_count(new_tags, out_file):
    out = open(out_file, 'w')
    for item in new_tags:
        out.write("%s" % item)
    out.close()

def usage():
    print """
    python rare_count_freqs.py [train_data]
    """

def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(2)

    # Calculate original word frequency
    count_frequency(sys.argv[1], './ner.counts')

    # Find rare words in the training data and replace them with '_RARE_'
    rare_words = find_rare('./ner.counts')
    new_tags = replece_rare(rare_words, sys.argv[1])
    output_new_count(new_tags, './new_ner_train.dat')

    # Re-calculate word frequency
    count_frequency('./new_ner_train.dat', './ner.counts')

if __name__ == "__main__":
    main()

