# The following code was written by Christopher Potts and Percy Liang. Their original file
# is called synthesis.py. We deleted evaluate_interpretive and evaluate_latent_semparse and
# adjusted evaluate_semparse and leaves as written in the comments in these functions.


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


def evaluate_semparse(u,lfs,grammar,allparses): # We give evaluate_semparse an utterance, an lf and a grammar as arguments so wen can use it for our interactive game  
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
                       eta=0.1)#0.1
    return weights # We return the weights so that we can use it for removing unlikely rules from the lexicon
    



if __name__ == '__main__':

    evaluate_semparse()

   

