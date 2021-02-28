# The following code was written by Christopher Potts and Percy Liang. Their original file
# is called synthesis.py. We deleted evaluate_interpretive and evaluate_latent_semparse and
# adjusted evaluate_semparse and leaves  as written in the comments in these functions.

#!/usr/bin/env python

"""
The intellectual core of the paper. For demos:

python synthesis.py

Our goal with this code is to illustrate how the learning framework
from `learning.py` and the grammar framework from `grammar.py` come
together.  

`phi_sem` is the simple feature function used in figure 2 of the paper.
We use it here for all of the illustrations.

`crude_lexicon` is a grammar that respects typing but nothing else.
Together with rules and functions from `grammar.py`, it defines a crude
grammar. The goal of learning is to refine this grammar by finding the
best pairings of lexical items and logical expressions.

For all of the illustrations, the train/test data are created in
`semdata` using a gold grammar, which has the same rules as the crude
grammar and the same functions for interpretation, but its lexicon is
perfect.

`evaluate_semparse` runs the semantic parsing model of section 4.1 of
the paper. Its training data predictions are perfect. It makes a
predictable mistake on the test data: since it never sees 'four'/4
in training, it gets the final test example wrong.

`evaluate_interpretive` implements section 4.2 of the paper, using
`LatentSGD` instead of `SGD` (both in `learning.py`). The role of the
grammar is the same as in `evaluate_semparse`, and the resulting
performance is the same as well.

`evaluate_latent_semparse` goes beyond what is in the paper, to
achieve more of a connection with published semantic parsing models.
Here, we see only the root node of the logical form in training, so
that the tree structure is a latent variable. To make it interesting,
we add a type-lifting rule to the grammar, so that many final logical
forms correspond to multiple distinct derivations. LatentSGD is used
for optimization, and the resulting performance is the same as for
the other models.

"""


__author__ = "Christopher Potts and Percy Liang"
__credits__ = []
__license__ = "GNU general public license, version 2"
__version__ = "2.0"
__maintainer__ = "Christopher Potts"
__email__ = "See the authors' websites"


import re
from collections import defaultdict
from grammar import Grammar, rules, functions
from learning import evaluate, SGD, LatentSGD
import semdata as semdata


def phi_sem(x, y):
    """Feature function defined over full trees. It tracks the topmost
    binary relation if there is one, and it tracks all the lexical 
    features."""
    d = defaultdict(float)
    # Topmost relation symbol:
    toprel_re = re.compile(r"^(and|exist)")
    #match = toprel_re.search(y[0][1])
    match = toprel_re.search(y.formular)
    if match:
        d[('top', 'R', match.group(1))] = 1.0
    # Lexical features:
    for leaf in y.components:
        d[leaf] += 1.0
    return d
    """
    for leaf in leaves(y):
        d[leaf] += 1.0
    return d"""

"""def leaves(x):
    #Recursive function for finding all the preterminals (mother--child)
    #trees. Used by phi_sem
    # Leaf-only trees:
    if len(x[1])==1 and isinstance(x[1][0],str):
        return [(x[0],x[1][0])] # Adjusted so it fit our backpointer implementation we build in the CYK-parser
    # Recursive call for all child subtrees:
    l = []
    for child in x[1]: # Adjusted so it fit to our backpointer implementation we build in the CYK-parser
        l += leaves(child)
    return l"""


def evaluate_semparse(u,lfs,grammar,allparses): # We give evaluate_semparse an utterance, an lf and a grammar as arguments so wen can use it for our interactive game
    """Evaluate the semantic parsing set-up, where we learn from and 
    predict logical forms. The set-up is identical to the simple 
    example in evenodd.py, except that classes is gram.gen, which 
    creates the set of licit parses according to the crude grammar."""    
    print("======================================================================")
    print("SEMANTIC PARSING")
    # Only (input, lf) pairs for this task:
    sem_utterance=[[u, lf, lf.semantic] for lf in lfs] # This replaces semdata
    semparse_train = [[x,y] for x, y, d in sem_utterance]
    semparse_test = [[x,y] for x, y, d in sem_utterance]        
    weights = evaluate(phi=phi_sem,      # We let evaluate return the weights and store them
                       optimizer=SGD,
                       train=semparse_train,
                       test=semparse_test,
                       classes=allparses,
                       true_or_false=grammar.sem,# We want only lf with denotation True. To test that we give this additional argument to evaluate
                       T=10,
                       eta=0.1)
    return weights # We return the weights so that we can use it for removing unlikely rules from the lexicon
    



if __name__ == '__main__':

    evaluate_semparse()

   

