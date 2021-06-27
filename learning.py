# The following code was written by Christopher Potts and Percy Liang. We adjusted
# evaluate  as written in the comments in this function. It implements the Stochastic
# Gradient Descent.



import re
import random
from collections import defaultdict
from operator import itemgetter
from itertools import product


def score(x=None, y=None, phi=None, w=None):
    """Calculates the inner product w * phi(x,y)."""
    return sum(w[f]*count for f, count in list(phi(x, y).items()))

def predict(x=None, w=None, phi=None, classes=None, output_transform=(lambda x : x)):    
    scores = [(score(x, y_prime, phi, w), y_prime) for y_prime in classes(x)]
    # Get the maximal score:
    max_score = sorted(scores)[-1][0]
    # Get all the candidates with the max score and choose one randomly:
    y_hats = [y_alt for s, y_alt in scores if s == max_score]
    return output_transform(random.choice(y_hats))


def SGD(D=None, phi=None, classes=None, true_or_false=None, T=10, eta=0.1, output_transform=None):
    w = defaultdict(float)
    for t in range(T):
        random.shuffle(D)
        for x, y in D:
            # Get all (score, y') pairs:
            #scores = [(score(x, y_alt, phi, w)+cost(y, y_alt), y_alt)
                      #for y_alt in classes(x)]
            scores = {y_alt:(score(x, y_alt, phi, w)+cost(y, y_alt)) for y_alt in classes}
            # Get the maximal score:
            max_score = max(list(scores.values()))
            # Get all the candidates with the max score and choose one randomly:
            y_tildes = [y_alt for y_alt in scores if scores[y_alt] == max_score]
            y_tilde = random.choice(y_tildes)
            # Weight-update (a bit cumbersome because of the dict-based implementation):
            actual_rep = phi(x, y)
            predicted_rep = phi(x, y_tilde)
            for f in set(list(actual_rep.keys()) + list(predicted_rep.keys())):
                w[f] += eta * (actual_rep[f] - predicted_rep[f])                             
    return w

def cost(y, y_prime):
    #return 0.0 if y.components == y_prime.components else 1.0 
    costs = [0.0 if x in y_prime.components else 1.0 for x in y.components] # We adjusted the cost function, so it fit better in our set up. You can see the original one in the line above.
    return sum(costs)/len(costs)

def evaluate(
        phi=None, 
        optimizer=None, 
        train=None, 
        test=None, 
        classes=None,
        true_or_false=None, # We add this argument
        T=10, 
        eta=0.1, 
        output_transform=(lambda x : x)):
    print("======================================================================")    
    print("Feature function: {}".format(phi.__name__))
    w = optimizer(
        D=train,
        phi=phi,
        T=T,
        eta=eta,
        classes=classes,
        true_or_false=true_or_false,
        output_transform=output_transform)
    print("--------------------------------------------------")
    print('Learned feature weights')

    for f, val in sorted(list(w.items()), key=itemgetter(1), reverse=True):
        print("{} {}".format(f, val))
    return w # We don't let the trained model predict the denotation of the test sentences, but return the learnded weights
    
    

