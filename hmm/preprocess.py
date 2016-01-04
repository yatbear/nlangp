#! /usr/bin/env python

__author__ = "yatbear <sapphirejyt@gmail.com>"
__date__ = "$Dec 21, 2015"

# Map the infrequent words (count < 5) to a common symbol _RARE_
def remap():
    # Read original training data
    trainset = [line.strip().split() for line in open('gene.train', 'r').readlines()]

    rare_candidates = dict()
    for sample in trainset:
        if len(sample) == 0:
            continue
        word = sample[0]
        if word in rare_candidates.keys():
            rare_candidates[word] += 1
        else:
            rare_candidates[word] = 1

    rarewords = list()
    for word, count in rare_candidates.iteritems():
        if count < 5:
            rarewords.append(word)

    new_trainset = list()
    for sample in trainset:
        if len(sample) == 0:
            new_trainset.append('\n')
            continue
            
        if sample[0] in rarewords:
            line = '_RARE_ ' + sample[1] + '\n' 
            new_trainset.append(line)
        else:
            line = sample[0] + ' ' + sample[1] + '\n'
            new_trainset.append(line)

    with open('gene1.train', 'w') as f:
        for line in new_trainset:
            f.write(line)


if __name__ == "__main__":
    remap()
