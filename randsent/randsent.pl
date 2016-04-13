#!/usr/bin/env perl

# @author yatbear
#         sapphirejyt@gmail.com
#
# Random sentence generator
# Generate sentences from context-free grammar
#
# Usage:
#       perl randsent.pl grammar_file num_sent
#       perl randsent.pl -t grammar_file num_sent | ./prettyprint

use strict;
use warnings;
no warnings "recursion";

my $filename = $ARGV[0] eq "-t" ? $ARGV[1] : $ARGV[0];
my $numSen = $ARGV[0] eq "-t" ? $ARGV[2] : $ARGV[1];
my %grammar;    # hashtable

# Read grammar file
open(my $file, "<:encoding(UTF-8)", $filename) || die "The grammar file cannot be opened! \n";
my @lines = <$file>;

foreach my $eachline(@lines) {
    chomp $eachline;
    if ($eachline =~ /^\s*#/) {
        next;
    }
    if ($eachline) {
        my @filter = split("#", $eachline);
        $eachline = $filter[0];
        my @tokens = split(" ", $eachline);
        my $key = $tokens[1];
        if ($key) {
            if (exists $grammar{$key}) {
                $grammar{$key} = $grammar{$key}."~~~".$eachline
            } else {
                $grammar{$key} = $eachline;
            }
        }
    }
}
close $file;

# Generate sentences
my $key = "ROOT";
if (!$numSen || $numSen == 0) {
    $numSen = 1;
}
if ($ARGV[0] ne "-t") {
    for (my $i=0; $i<$numSen; $i++) {
        my $sent = genSent($key);
        print "$sent\n\n";
    }
} else {
    for (my $i=0; $i<$numSen; $i++) {
        genTree($key);
        print "\n\n";
    }
}

# Select a grammar rule based on probabilities
sub selectRule {
    my @rules = @_;
    my $range = 0;
    my @ruleRange;
    foreach my $i (0 .. $#rules) {
        my @tokens = split (" ", $rules[$i]);
        $range = $range + $tokens[0];
        $ruleRange[$i] = $tokens[0];
    }
    srand;
    my $n = rand($range);
    my $sum = 0;
    for (my $j=0; $j<@rules; $j++) {
        if ($n >= $sum && $n < $sum + $ruleRange[$j]) {
          return $j;
        }
        $sum = $sum + $ruleRange[$j];
    }
}

# Sentence generator
sub genSent {
    my $sent = "";
    my $key = $_[0];
    if (!exists $grammar{$key}) {
        return $key;
    } else {
        my $rules = $grammar{$key};
        my @ruleList = split("~~~", $rules);
        my $ruleIndex = 0;
        if (@ruleList > 1) {
            $ruleIndex = selectRule(@ruleList);
        }
        my $rule = $ruleList[$ruleIndex];
        my @ele = split(" ", $rule);
        my $word;
        for (my $i=2; $i<@ele; $i++) {
            if (exists $grammar{$key}) {
                $word = genSent($ele[$i]);
            }
            if ($sent ne "") {
                $sent = $sent." ";
            }
            $sent = $sent.$word;
        }
        return $sent;
    }
}

# Generate the treeviews of sentences
sub genTree {
    my $key = $_[0];
    if (exists $grammar{$key}) {
        if ($key ne "ROOT") {
            print " ";
        }
        print "\($key";
        my $rules = $grammar{$key};
        my @ruleList = split("~~~", $rules);
        my $ruleIndex = 0;
        if (@ruleList > 1){
            $ruleIndex = selectRule(@ruleList);
        }
        my $rule = $ruleList[$ruleIndex];
        my @ele = split(" ", $rule);
        for (my $i=2; $i<@ele; $i++) {
            genTree($ele[$i]);
        }
        print "\)";
    } else {
        print " $key";
    }
}