## Earley Parser

A dynamic parser for context-free languages based on [Earley's algorithm](https://en.wikipedia.org/wiki/Earley_parser). 

This is a chart parser that uses dynamic programming. The grammar rules are written left-recursively. 
    
    Usage:      python parser.py grammar_file sentence_file | ./prettyprint
    
    Example:    python parser.py papa.gr papa.sen | ./prettyprint
    
    
Example output:

<img src="https://github.com/yatbear/nlangp/blob/master/EarleyParser/data/output.png" width=500/>
