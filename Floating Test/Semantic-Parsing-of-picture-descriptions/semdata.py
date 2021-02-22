#!/usr/bin/env python

"""
This file contains the training and test sentences used for developing,
testing and debugging our grammar for SHAPELURN
The functions at the end generate a training data set and a test data set
based on the gold lexicon and the grammar in grammar.py
The code is taken from Christopher Potts and Percy Liang (see below) and
we replaced their train and test utterances with our sentences
"""

__author__ = "Christopher Potts and Percy Liang"
__credits__ = []
__license__ = "GNU general public license, version 2"
__version__ = "2.0"
__maintainer__ = "Christopher Potts"
__email__ = "See the authors' websites"


from grammar import *


# Gold grammar for creating the data:
gram = Grammar(gold_lexicon, rules, functions)

# Train/test data for the demo:
train_utterances = [
    'there are two blue squares',
    'there is one yellow form',
    'there are two blue squares and there is one blue triangle',
    'there are three squares',
    'there is a red triangle',
    'there are two triangles',
    'there is one blue triangle and there is one red triangle',
    'there are two triangles and there is a yellow square',
    'there is a blue square',
    'there are two blue squares',
    'there is one yellow square',
    'there is a blue form',
    'there is one red form'
]

# Test:
# Test Utterances for world.jpg
test_utterances = [
    'there is a red triangle under a blue square',
    'there is a red circle under a blue square',
    'there are two blue squares',
    'there are two triangles',
    'there are three blue forms',
    'there is one blue form', 
    'there is a red triangle and there is a blue triangle',
    'there is a blue square over a red triangle',
    'there is a blue square over a yellow square over a red triangle',
    'there is a blue square next to a blue square',
    'there is a blue square over a yellow square over a blue triangle', 
    'there is a red triangle under a blue triangle under a blue square',
    'there is a red triangle under a yellow square under a blue triangle', 
    'there is a yellow square to the left of a blue triangle',
    'there is a yellow square to the right of a blue triangle'
    ]

# should all evaluate to true
test_utterances = [
    'there is a blue triangle',
    'there is a red triangle',
    'there is a blue square',
    'there is a yellow square',
    'there are two blue squares',
    'there are three squares',
    'there are two triangles',
    'there is a red triangle under a blue square',
    'there is a blue square over a yellow square',
    'there is a yellow square next to a blue triangle',
    'there is a blue square over a blue triangle over a red triangle'
]

# Test Utterances for world2.jpg

# Are all working
test_utterances = [
    'there is a square',
    'there are three blue circles',
    'there are two red triangles',
    'there is a green square',
    'there is a yellow triangle',
    'there is a yellow form',
    'there is a yellow triangle and there is a green square',
    'there is a yellow triangle and there is a yellow circle',
    'there is a yellow triangle and there is a red triangle',
    'there is a green circle over a green circle',
    'there is a green triangle under a red circle',
    'there is a green circle to the right of a red circle',
    'there is a green form next to a green form',
    'there is a blue circle under a blue circle',
    'there is a yellow circle over a blue circle',
    'there is a red triangle over a yellow triangle',
    'there is a yellow triangle under a red triangle',
    'there is a red triangle under a yellow triangle',
    'there is a yellow triangle over a red triangle',
    'there is a blue triangle under a red triangle under a yellow triangle',
    'there are two green circles under three blue circles',
    'there are two green circles under two blue circles',
    'there are two green circles under a blue circle',
    'there is a blue circle over a yellow circle',
    'there is a blue circle over two yellow circles',
    'there is a blue circle over one yellow circle',
    'there are two green circles under one yellow circle under a red circles'
]

test_utterances = [
    'there is a blue triangle under a red triangle under a yellow triangle'
    ]



test_utterances_new = [
    'there is a red square or there is a green square',
    'there is a red circle or there is a yellow circle'
    ]

test_utterances_flex = [
    'there there is a green circle to the left of a green triangle',
    'is a green circle to the left of a green triangle',
    'is a circle green to the left of a triangle green',
    'there is a green circle left of a green triangle',
    'there there is a circle green to left of a triangle green',
    'a green circle to the left of a green triangle there is'
    ]



"""
# This is a list of triples (x, y, d), where x is an input string, y
# is its preferred logical form, and d is the denotation of the
# logical form y. The semantic parsing algorithms use only x and y,
# and the interpretive algorithms use only x and d.
sem_train = []
for u in train_utterances:
    # Pick the first in the list of possible LFs, since this happens
    # to correspond to the preferences we expressed in the paper:
    lf = gram.gen(u)[0] 
    sem_train.append([u, lf, gram.sem(lf)])


# A list of triples with the same format as the training data; the
# algorithms should do well on the first three and fail on the last
# one because 'four'/4 never appears in the training data.
sem_test = []
for u in test_utterances:
    # Pick the last in the list of possible LFs, since this happens to 
    # correspond to the preferences we expressed in the paper:
    lf = gram.gen(u)[-1]
    sem_test.append([u, lf, gram.sem(lf)])
"""

