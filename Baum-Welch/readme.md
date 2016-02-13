## HMMs and Baum-Welch

Model letters of English text using Hidden Markov Models:

- Implement Baum-Welch algorithm on a two-state HMM.

- Train text A to estimate the transition probabilities p and the emission probabilities q.

- Iteration time: 600


### Data

The text is 35000 characters long, and has been divided into a 30000 character training set, named A, and a 5000 character test set, named B. 

All numerals and punctuation have been purged, capital letters have been down-cased, and inter-word spacing, new lines and paragraph breaks, have all been normalized to single spaces. The alphabet of the resulting text is therefore the 26 lower-case English letters and the white-space.