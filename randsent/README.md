## Random Sentence Generator

Randomly generate sentences based on context-free grammars using Depth-First expansion.

For the purpose of CFG design.


### Generate random sentences
    
    Usage:      perl randsent.pl grammar_file num_sent
    
    Example:    perl randsent.pl grammar 5


### Generate sentence treeviews
    
    Usage:      perl randsent.pl -t grammar_file num_sent | ./prettyprint
    
    Example:    perl randsent.pl -t grammar 2 | ./prettyprint