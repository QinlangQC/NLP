'''
    Word tagger for question 4 in homework 1
'''
import sys
import math

class Varables: # store all vectors needed
    def __init__(self):
        self.emission_prob = {}
        self.all_words = {}
        self.x_yx = {}
        self.yx_y = {}

def emission(file): # calculate the emission probability vector
    input = open(file, 'r')
    lines = input.readlines()
    count_yx_dict = {} # Number of times a tag_word pair appears in the training set
    count_y_dict = {} # Number of times a tag appears in the training set
    yx_y = {} # Store the tag for a tag_word pair
    x_yx = {} # Store the tag_word pairs for a word
    emission_prob = {}
    for line in lines:
        if line.find('WORDTAG') == -1:
            continue
        line = line.rstrip()
        words = line.split(' ')
        yx = words[2] + ' ' + words[3]
        count_yx_dict[yx] = int(words[0])
        yx_y[yx] = words[2]
        if words[2] in count_y_dict:
            count_y_dict[words[2]] += int(words[0])
        else:
            count_y_dict[words[2]] = int(words[0])
        if words[3] in x_yx:
            if yx not in x_yx[words[3]]:
                x_yx[words[3]][yx] = None
        else:
            x_yx[words[3]] = {}
            x_yx[words[3]][yx] = None
    for key in count_yx_dict:
        emission_prob[key] = math.log(count_yx_dict[key], 2) - math.log(count_y_dict[yx_y[key]], 2)
    return emission_prob, x_yx, yx_y

def count_words(file): # count the times of appearance of words in the test set
    input = open(file, 'r')
    lines = input.readlines()
    all_words = {}
    for line in lines:
        line = line.rstrip()
        if line == '':
            continue
        if line in all_words:
            all_words[line] += 1
        else:
            all_words[line] = 1
    return all_words

def predict(file, vars): # make prediction using the emission probability
    input = open(file, 'r')
    lines = input.readlines()
    output = []
    for word in lines:
        word = word.rstrip()
        if word == '':
            output.append(word)
            continue
        orig = word
        max = float('-inf')
        tag = 'O'
        if word not in vars.x_yx:
            word = '_RARE_'
        for key in vars.x_yx[word]:
            if vars.emission_prob[key] > max:
                max = vars.emission_prob[key]
                tag = vars.yx_y[key]
        output.append(orig + ' ' + tag + ' ' + str(max))
    return output

def output(file, out): # output prediction result
    for item in out:
        file.write('%s\n' % item)

def usage():
    print """
    python tagger.py [test_data] [train_counts] > [prediction_file]
    """

def main():
    if len(sys.argv) != 3:
        usage()
        sys.exit(2)

    vars = Varables()
    vars.emission_prob, vars.x_yx, vars.yx_y = emission(sys.argv[2])
    vars.all_words = count_words(sys.argv[1])
    out_put = predict(sys.argv[1], vars)
    output(sys.stdout, out_put)

if __name__ == "__main__":
   main()