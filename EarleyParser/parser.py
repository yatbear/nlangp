#!usr/bin/env python
# -*- coding: utf-8 -*-

# Usage: python parser.py grammar_file sentence_file | ./prettyprint
# 
# A Parser based on weighted Earley's Algorithm
#
# Author: yatbear <sapphirejyt@gmail.com>
#         2016-04-11

from __future__ import division
from collections import defaultdict
import sys
import math

class Rule(object):
    '''
    Grammar Rule
    '''
    def __init__ (self, lhs, rhs, prob):
        '''
        Args:
            lhs: left hand side of the rule
            rhs: right hand side of the rule
            weight: entry weight (negative log-likelihood)
        '''
        self.lhs = lhs
        self.rhs = rhs
        self.weight = -math.log(float(prob)) / math.log(2.0) # to prevent underflow
        
class Entry:
    '''
    Parsing chart entry
    '''
    def __init__(self, column, lhs, rhs, weight, ancestors):
        '''
        Args:
            column: column index of the entry
            lhs: left hand side of the corresponding rule
            rhs: right hand side of the corresponding rule
            weight: entry weight (negative log-likelihood)
            ancestors: previous entries that derive the current entry
        '''
        self.column = column
        self.lhs = lhs
        self.rhs = rhs
        self.weight = weight
        self.ancestors = ancestors
    
    def __getitem__(self, key):
        if self.ancestors:
            return self.ancestors[key]

class EarleyParser(object):
    
    def __init__(self):
        self.sentences = list() # sentences to parse
        self.rules = list() # grammar rules 
        self.R = defaultdict() # prefix table

    def readSents(self, sent):
        '''
        Read sentences from the sentence file
        Args:
            sent: sentence file (.sen)
        '''
        lines = [line.strip() for line in open(sent, 'r').readlines()]
        sentences = list()
        for line in lines:
            if line:
                self.sentences.append(line)
    
    def readGrammars(self, gra):
        '''
        Extract rules from the given grammar file
        Build the prefix table 
        Args:
            gra: grammar file (.gr)
        '''
        grammars = [line.strip() for line in open(gra, 'r').readlines()]
        for line in grammars:
            if line.split()[0] == '#':
                continue
            [prob, lhs], rhs = line.split()[:2], line.split()[2:]
            rule = Rule(lhs, rhs, prob)
            self.rules.append(rule)
            # Store the rules into the prefix table R
            if lhs not in self.R:
                self.R[lhs] = [rule]
            else:
                self.R[lhs].append(rule)
    
    def getEntries(self, lhs):
        '''
        Create entries according to the left hand side of the given rule
        Args:
            lhs: left hand side of a grammar rule
        Returns:
            a list of chart entries
        '''
        entries = list()
        for rule in self.rules:
            if rule.lhs == lhs:
                newEntry = Entry(0, rule.lhs, rule.rhs[:], rule.weight, None)
                entries.append(newEntry)
        return entries
        
    def isTerminal(self, lhs):
        '''
        Check if the given lhs is a terminal
        '''
        return not self.R.has_key(lhs)
        
    def expand(self, entry, col):
        '''
         Expand the first non-terminal on the rhs of the given enrty
         Args:
             entry: a chart entry
             col: chart column number
         Returns:
             a list of chart entries
        '''
        lhs = entry.rhs[0]
        entries = self.getEntries(lhs)
        for entry in entries:
            entry.column = col
        return entries
        
    def addEntry(self, column, entry):
        '''
        Add one entry to the column
        Args:
            column: one chart column 
            entry: one chart entry
        Return:
            Updated column
        '''
        exist = False
        for en in column:
            if en.lhs == entry.lhs and en.rhs == entry.rhs:    
                if en.column == entry.column: 
                    exist = True
                    if en.weight > entry.weight:
                        en.weight = entry.weight
                if en.weight == entry.weight:
                    exist = True
                    if en.column < entry.column:
                        en.column = entry.column
        if not exist:
            column.append(entry)
        return column
        
    def addEntries(self, column, newEntries):
        '''
        Add new entries to the column
        Args:
            column: one chart column 
            newEntries: a list of chart entries
        Return:
            Updated column
        '''
        for entry in newEntries:
            column = self.addEntry(column, entry)
        return column
        
    def scan(self):
        '''
        Scan for the next word
        '''
        word = ''
        if self.sentences:
            sentence = self.sentences[0]
            if sentence:
                word = sentence.split()[0]
        return word
        
    def updateSents(self):
        '''
        Update unprocessed sentences
        Remove the most recently processed word
        '''
        if self.sentences:
            words = self.sentences[0].split()
            words.pop(0)
            self.sentences[0] = ' '.join(words)
    
    def printParsed(self, entry):
        '''
        Display the parsed result
        '''
        if not entry.ancestors:
            print '(',
            print entry.lhs + ' ',
            if self.isTerminal(entry.rhs[0]):
                print entry.rhs[0],
        else:
            self.printParsed(entry.ancestors[0])
            if len(entry.ancestors) > 1:
                self.printParsed(entry.ancestors[1]),
                print ')',
            # Print the non-Terminals on the rhs of the entry
            if len(entry.rhs) > 0:
                if self.isTerminal(entry.rhs[0]):
                    print entry.rhs[0],
            if entry.lhs == 'ROOT':
                print ')'
    
    def parse(self):
        '''
        Parsing procedure:
                1. Attach
                2. Scan
                3. Predict
        '''
        # Find the ROOT entries and place them in column 0
        root = self.getEntries('ROOT')
        table = [root] # a parsing chart: a list of columns 
        done = False
        i = 0 # current column index
        for column in table:
            # Check the state of the rhs of each entry (check the location of the dot)
            for entry in column:
                word = self.scan() # look ahead, eliminate unnecessary predictions
                  ############
                 #  Attach  #
                ############
                if not entry.rhs:
                    if entry.lhs == 'ROOT':
                        # If all the inputs have been scanned and this is the last column of the table
                        if not self.sentences[0] and len(table) == i+1:
                            done = True
                            self.printParsed(entry) # print the parsed tree
                            print entry.weight # print the weight of the parsed tree
                            break
                    else:
                        col = table[entry.column]
                        for oldEntry in col:
                            if oldEntry.rhs and oldEntry.rhs[0] == entry.lhs:
                                rhs = oldEntry.rhs[:]
                                rhs.pop(0)
                                weight = oldEntry.weight + entry.weight
                                ancestors = [oldEntry, entry]
                                newEntry = Entry(oldEntry.column, oldEntry.lhs, rhs, weight, ancestors)
                                column = self.addEntry(column, newEntry)
                  ##########
                 #  Scan  #
                ##########
                elif self.isTerminal(entry.rhs[0]):
                    word = self.scan()
                    if word:
                        # If scan succeeds
                        if entry.rhs[0] == word:
                            # Add a new column to the table, place the current entry in the new column
                            newColumn = list()
                            rhs = entry.rhs[:]
                            rhs.pop(0)
                            ancestor = [entry]
                            newEntry = Entry(entry.column, entry.lhs, rhs, entry.weight, ancestor)
                            if len(table) == i+1:
                                if newEntry not in newColumn:
                                    newColumn.append(newEntry)
                                table.append(newColumn)
                                self.updateSents()
                            else:
                                table[i+1] = self.addEntry(table[i+1], newEntry)
                  #############
                 #  Predict  #
                #############
                elif not self.isTerminal(entry.rhs[0]):
                    # Check if the current entry has already been predicted
                    predicted = False
                    for en in column:
                        if en.column == i: # if c is predicted and added to the column i
                            if en.lhs == entry.rhs[0]:
                                predicted = True
                                break
                    if not predicted:
                        # Expand current entry and add derived entries to this column
                        newEntries = self.expand(entry, i)
                        column = self.addEntries(column, newEntries)
            i += 1 # keep track of current column index
            if done:
                break
        # Parsing trees do not exist.
        if not done:
            print 'None'
    
    def driver(self, gra, sent):
        '''
        Driver function of the parser
        Args:
            gra: grammar file (.gr)
            sent: sentence file (.sen)
        '''
        self.readSents(sent)
        self.readGrammars(gra)
        while self.sentences:
            self.parse()
            self.sentences.pop(0)

def main():
    if len(sys.argv) != 3:
        gr, sen = 'data/papa.gr', 'data/papa.sen' 
    else:  
        gr, sen = sys.argv[1:]
    parser = EarleyParser()
    parser.driver(gr, sen)

if __name__ == '__main__':
    main()