#! /usr/bin/env python

__author__ = "yatbear <sapphirejyt@gmail.com>"
__date__ = "$Dec 20, 2015"

from math import log

# Collect counts
def collect_counts(counts):
    ecounts = dict()   # emission counts
    unicounts = dict() # unigram counts 
    bicounts = dict()  # bigram counts
    tricounts = dict() # trigram counts

    for line in counts:
        count, lbl = float(line[0]), line[1]
        # Collect emission counts 
        if lbl == 'WORDTAG':
            tag, word = line[2], line[3]
            key = word + '|' + tag
            ecounts[key] = count
        # Collect unigram counts
        elif lbl == '1-GRAM':
            tag = line[2]
            unicounts[tag] = count
        # Collect bigram counts
        elif lbl == '2-GRAM':
            key = line[2] + ',' + line[3]
            bicounts[key] = count
        # Collect trigram counts
        elif lbl == '3-GRAM':
            key = line[2] + ',' + line[3] + ',' + line[4]
            tricounts[key] = count

    return ecounts, unicounts, bicounts, tricounts

# A simple gene tagger, maximize the emission probability
def simple_tagger(devset, ecounts, unicounts): 
    tag_results = list() 
    tags = unicounts.keys()
    
    for sample in devset:
        if len(sample) == 0:
            tag_results.append('\n') # to align with the dev file
            continue

        word = sample[0]
        best_tag, maxp = None, -1

        # Maximize emission probability 
        for tag in tags:
            key = word + '|' + tag
            ecount = ecounts[key] if key in ecounts.keys() else 0.0
            # e(word|tag) = Count(tag->word) / Count(tag)
            eprob = ecount / unicounts[tag] 
            if eprob > maxp:
                best_tag, maxp = tag, eprob

        tagline = word + ' ' + best_tag + '\n'
        tag_results.append(tagline)

    with open('gene_dev.p1.out', 'w') as f:
        for line in tag_results:
            f.write(line)

# Viterbi gene tagger
def viterbi_tagger(devset, ecounts, unicounts, bicounts, tricounts):
    tags = unicounts.keys()
    tag_results = list()

    for sample in devset:
        if len(sample) == 0: 
            continue
        x_seq = sample.split('\n')
        n = len(x_seq)

        pi = dict() # pi table
        bp = dict() # back pointers
        
        pi['0,*,*'] = 0.0 # initial pi (log probability)
        
        # Compute pi table entries
        def compute_pi(k, x, w, u, v):
            key0 = str(k-1) + ',' + w + ',' + u
            pi_lp0 = pi[key0]

            trikey = w + ',' + u + ',' + v
            bikey = u + ',' + v  
            qprob = tricounts[trikey] / bicounts[bikey] 

            ekey = x + '|' + v 
            if ekey in ecounts.keys():
                eprob = ecounts[ekey] / unicounts[v] 
            else:
                rarekey = '_RARE_|' + v               
                eprob = 1e-5 * ecounts[rarekey] / unicounts[v] 

            # Take log probabilities to prevent underflow
            pi_lp = pi_lp0 + log(qprob) + log(eprob)

            return pi_lp

        # Decode gene sequence
        for k, x in enumerate(x_seq):
            k += 1     
            if k == 1:
                w, u = '*', '*'
                for v in tags:
                    key = str(k) + ',' + u + ',' + v
                    pi[key] = compute_pi(k, x, w, u, v)
            elif k == 2:
                w = '*'
                for u in tags:
                    for v in tags:
                        key = str(k) + ',' + u + ',' + v
                        pi[key] = compute_pi(k, x, w, u, v)
            else:
                for u in tags:
                    for v in tags:
                        best_w, maxlp = None, -float('inf')
                        # Choose w to maximize pi 
                        for w in tags:
                            pi_lp = compute_pi(k, x, w, u, v)
                            if pi_lp > maxlp:
                                maxlp = pi_lp
                                best_w = w   
                        key = str(k) + ',' + u + ',' + v
                        pi[key] = maxlp
                        bp[key] = best_w

        last2tags = list()
        maxlp = -float('inf')

        # Set the last two tags
        for u in tags:
            for v in tags:
                key = str(n) + ',' + u + ',' + v    
                pi_lp = pi[key] # if key in pi.keys() else -float('inf')
                trikey = u + ',' + v + ',STOP'
                bikey = v + ',STOP' 
                qprob = tricounts[trikey] / bicounts[bikey] 
                lp = pi_lp + log(qprob)
                if lp > maxlp:
                    maxlp = lp 
                    last2tags = [u, v]
                    
        [u, v] = last2tags
        inv_tag_seq = [v, u] # inverse tag sequence

        # Tag in backward manner
        for k in xrange(n-2, 0, -1):
            key = str(k+2) + ',' + u + ',' + v
            w = bp[key]
            inv_tag_seq.append(w)
            u, v = w, u

        for k, x in enumerate(x_seq):
            y = inv_tag_seq[n-k-1]
            tagline = x + ' ' + y + '\n'
            tag_results.append(tagline)

        tag_results.append('\n')
    
    # Write the tagging result to file    
    with open('gene_dev.p2.out', 'w') as f:
        for line in tag_results:
            f.write(line)

def main():    
    # Collect counts
    counts = [line.strip().split() for line in open('gene.counts', 'r').readlines()]
    ecounts, unicounts, bicounts, tricounts = collect_counts(counts)
    # Unigram Tagger
    devset = [line.strip().split() for line in open('gene.dev', 'r').readlines()]
    simple_tagger(devset, ecounts, unicounts)
    # Viterbi Tagger
    devset = open('gene.dev', 'r').read().split('\n\n') # read sequences
    viterbi_tagger(devset, ecounts, unicounts, bicounts, tricounts)

if __name__ == "__main__":
    main()