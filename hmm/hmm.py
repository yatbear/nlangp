#! /usr/bin/env python

__author__ = "yatbear <sapphirejyt@gmail.com>"
__date__ = "$Dec 20, 2015"

# A simple gene tagger, maximize the emission probability
def unigram_tagger(devset, counts):
    ecounts = dict() # emission counts
    unicounts = dict() # unigram counts 
    
    # Collect emission and unigram counts
    for line in counts:
        count, lbl, tag = float(line[0]), line[1], line[2]
        if lbl == 'WORDTAG':
            word = line[3]
            key = word + '|' + tag
            ecounts[key] = count
        elif lbl == '1-GRAM':
            unicounts[tag] = count

    tags = list()
    for sample in devset:
        if len(sample) == 0:
            tags.append('\n') # to align with the dev file
            continue

        word = sample[0]
        best_tag, maxp = None, -1

        # Maximize emission probability 
        for tag in unicounts.keys():
            # e(word|tag) = Count(tag->word) / Count(tag)
            key = word + '|' + tag
            ecount = ecounts[key] if key in ecounts.keys() else 0.0
            eprob = ecount / unicounts[tag]
           
            if eprob > maxp:
                best_tag, maxp = tag, eprob

        tagline = word + ' ' + best_tag + '\n'
        tags.append(tagline)

    with open('gene_dev.p1.out', 'w') as f:
        for line in tags:
            f.write(line)

def main():    
    devset = [line.strip().split() for line in open('gene.dev', 'r').readlines()]
    counts = [line.strip().split() for line in open('gene.counts', 'r').readlines()]

    unigram_tagger(devset, counts)

if __name__ == "__main__":
    main()
