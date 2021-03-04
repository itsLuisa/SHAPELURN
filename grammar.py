#!/usr/bin/env python

"""
Defines our grammar: the lexicon (which actually is not used in the game when learning from scratch), the CFG rules
and the functions on how to evaluate the logical forms with respect to a current Picture Object
It also includes the CKY parser used to parse the input utterances and convert into logical forms
Does only work in combination with simple_gui.py and NOT with simple_gui_floating.py

Terminology:
Difference between referenced and guessed blocks:
for sentences like "there is a red circle" both refer to the same Block objects, i.e. the objects of all red circles in the Picture
but for e.g. the sentence "there is a green triangle over a red square over a circle" referenced blocks consists of
all green triangles that are over red squares that are over any circle
whereas guessed blocks consists of all green triangles, red squares and circles that make this sentence true
"""

import sys
from collections import defaultdict
from itertools import product
from eval_helper import *

# variable to store all blocks of the current picture
allblocks = []
# variable to store the guessed blocks for an input utterance
guessed_blocks = set()
# only needed when running this script separately for demo or testing purpose
all_blocks_grid = []

def create_all_blocks(picture):
    """
    updates the allblocks by resetting and then adding all blocks of the Picture object
    :param picture: a Picture object as defined in BlockPictureGenerator.py
    :return: None
    """
    allblocks.clear()
    grid = picture.grid
    for row in grid:
        for b in row:
            if b:
                allblocks.append(b)            
    return None

def update_guess(blocks):
    """
    updates the guessed_blocks variable by adding the referenced blocks and additionally
    recursively backtracking all matching blocks in order to get the complete list of guessed blocks
    :param blocks: list of Block objects, i.e. the referenced blocks
    :return: True
    """
    guesses = set()
    stack = blocks.copy()

    while stack != []:
        b = stack.pop()
        guesses.add(b)
        stack.extend(b.back_track)
        b.back_track = []
    for b in allblocks:
        b.back_track = []
    guessed_blocks.update(set(guesses))
    return True


def create_lex_rules():
    """
    creates the crude lexical rules for learning from scratch
    :return: list containing all lists from gold lexicon with the (category, logical form) tuples
    """
    crude_rules = set()
    for key, value in gold_lexicon.items():
        crude_rules.add(value[0])
        
    return list(crude_rules)



class ParseItem:
    """
    Objects representing the logical formulas that the parser builds up step by step
    c: string, category of the formular
    s: int, size of the formula (= out of how many subformulas it is built)
    semantic: Truth value of the formula when evaluated with respect to a picture; None if the formula is not a complete
                formula, i.e. if c is not "V"
    components: set of pairs of words from the utterance and the lexical rule paired with it by the parser
    formular: string representation of the formula
    guessed_blocks: list of Block Objects, list of the guessed blocks when formular is evaluate w.r.t a given picture
                    the list is empty if formula is not complete yet, i.e. if c is not "V"
    """
    def __init__(self,categorie,length,semantic,components,str_form,guesses):
        self.c = categorie
        self.s = length
        self.semantic = semantic
        self.components = components
        self.formular = str_form
        self.guessed_blocks = guesses


"""
The framework below is taken from Potts & Liang
We defined our own lexicon, rules and  functions and extended the main function demonstrating our grammar framework
The Grammar class was taken from Potts & Liang and we adapted the CKY parser by adding backpointers and added the 
methods needed to use the backpointers and recursively build the tree
allcombos and sem were not changed by us
"""

class Grammar:

    def __init__(self, lexicon, rules, functions):
        """For examples of these arguments, see below."""
        self.lexicon = lexicon
        self.rules = rules
        self.functions = functions
        self.backpointers = defaultdict(list)

    def recursive_treebuild(self, current):
        """
        recursively builds up the tree parse tree based on self.backpointers
        :param current: triple consisting of (Nonterminal, start_index, end_index) for which the trees with the
                        root Nonterminal that covers the input from start_index to end_index should be build
        :return: list of all possible trees with root Nonterminal covering start_index to end_index
        """
        current_label = current[0]
        current_start = current[1]
        current_end = current[2]
        sub_trees = []
        if current_end - current_start == 1:
            leaf = self.backpointers[current]
            tree = [current_label, leaf]
            sub_trees.append(tree)
        else:
            possible_children = self.backpointers[current]
            for pointer in possible_children:
                child1 = pointer[0]
                child2 = pointer[1]
                k = pointer[2]
                left_subtrees = self.recursive_treebuild((child1, current_start, k))
                right_subtrees = self.recursive_treebuild((child2, k, current_end))

                for left in left_subtrees:
                    for right in right_subtrees:
                        tree = [current_label, [left, right]]
                        sub_trees.append(tree)

        return sub_trees


    def compute_parse_trees(self, n):
        """
        computes the parse trees rooted in the start symbol V and spanning words from position 0 to n
        which corresponds to the whole input utterance
        :param n: int length of the string that should be covered by the tree + 1
        :return: list of all parse trees
        """
        parse_trees = []
        for l, x, y in self.backpointers:
            if l[0] == "V" and x == 0 and y == n:
                parse_trees += self.recursive_treebuild((l, x, y))
        return parse_trees


    def gen(self, s):
        """CYK parsing, but we just keep the full derivations. The input
        s should be a string that can be parsed with this grammar."""
        words = s.split()
        n = len(words) + 1
        trace = defaultdict(set)
        self.backpointers = defaultdict(list)

        for i in range(1, n):
            word = words[i - 1]
            for syntax, semantic in self.lexicon[word]:
                trace[(i - 1, i)].add((syntax, semantic))
                self.backpointers[((syntax, semantic), i - 1, i)].append(word)

        for j in range(2, n):
            for i in range(j - 1, -1, -1):
                for k in range(i + 1, j):
                    for c1, c2 in product(trace[(i, k)], trace[(k, j)]):
                        for lfnode in self.allcombos(c1, c2):
                            trace[(i, j)].add(lfnode)
                            self.backpointers[(lfnode, i, j)].append((c1, c2, k))
        # Return only full parses, from the upper right of the chart:
        results = []
        parse_trees = self.compute_parse_trees(n-1)
        for lf in parse_trees:
            category = lf[0][0]
            formular = lf[0][1]
            l = n
            p_item = ParseItem(category, n, None, set(), formular, None)
            p_item.semantic = self.sem(p_item)
            p_item.guessed_blocks = guessed_blocks.copy()
            guessed_blocks.clear()
            results.append(p_item)
            
        return results
        #return self.compute_parse_trees(n - 1)

    def allcombos(self, c1, c2):
        """Given any two nonterminal node labels, find all the ways
        they can be combined given self.rules."""
        results = []
        for left, right, mother, app_order in self.rules:
            if left == c1[0] and right == c2[0]:
                sem = [c1[1], c2[1]]
                results.append((mother, "{}({})".format(
                    sem[app_order[0]], sem[app_order[1]])))
        return results

    def sem(self, lf):
        """Interpret, as Python code, the root of a logical form
        generated by this grammar."""
        # Import all of the user's functions into the namespace to
        # help with the interpretation of the logical forms.
        grammar = sys.modules[__name__]
        for key, val in list(self.functions.items()):
            setattr(grammar, key, val)
        return eval(lf.formular)
        #return eval(lf[0][1])  # Interpret just the root node's semantics.


# The lexicon for our pictures
# Lexicon maps strings to list of tuples of (category, logical form)
gold_lexicon = {
    'form':[('B', 'block_filter([], allblocks)')],
    'forms':[('B', 'block_filter([], allblocks)')],
    'square': [('B', 'block_filter([lambda b: b.shape=="rectangle"],allblocks)')],
    'squares': [('B', 'block_filter([lambda b: b.shape=="rectangle"], allblocks)')],
    'triangle': [('B', 'block_filter([(lambda b: b.shape == "triangle")], allblocks)')],
    'triangles': [('B', 'block_filter([(lambda b: b.shape == "triangle")], allblocks)')],
    'circle': [('B', 'block_filter([(lambda b: b.shape == "circle")], allblocks)')],
    'circles': [('B', 'block_filter([(lambda b: b.shape == "circle")], allblocks)')],
    'green': [('C', 'green')],
    'yellow': [('C', 'yellow')],
    'blue': [('C', 'blue')],
    'red': [('C', 'red')],
    'there': [('E', 'identity')],
    'is': [('I', 'exist')],
    'are': [('I', 'exist')],
    'a':[('N','range(1,17)')],
    'one':[('N','[1]')],
    'two':[('N','[2]')],
    'three':[('N','[3]')],
    'under': [('U', 'under')],
    'over': [('U', 'over')],
    'and': [('AND', 'und')],
    'or': [('AND', 'oder'),('AND','xoder')],
    'next': [('NEXT', 'next')],
    'to': [('TO', 'identity')],
    'of': [('TO', 'identity')],
    'left': [('LR', 'left')],
    'right': [('LR', 'right')],
    'the': [('THE', 'identity')]

}

# The binarized rule set for our pictures, start symbol is V
# each entry is a list of four elements ['B', 'C', 'A', (i,j)]
# where A is the parent category, B the left child and C the right child
# (i,j) states that the logical form of the ith element is applied to the locigal form of the jth element
# e.g. The first rule corresponds to: V -> EN  B  and specifies that EN is applied to B: EN(B)
rules = [
    ['EN', 'B', 'V', (0, 1)],
    ['EN', 'BS', 'V', (0, 1)],
    ['VAND', 'V', 'V', (0, 1)],
    ['I', 'N', 'EN', (0, 1)],
    ['E', 'I', 'I', (0, 1)],
    ['C', 'B', 'B', (0, 1)],
    ['B', 'L', 'BS', (1, 0)],
    ['POS', 'B', 'L', (0, 1)],
    ['POS', 'BS', 'L', (0, 1)],
    ['U', 'N', 'POS', (0, 1)],
    ['PP', 'N', 'POS', (0, 1)],
    ['NEXT', 'TO', 'PP', (1, 0)],
    ['TS', 'SIDE', 'PP', (0, 1)],
    ['TO', 'THE', 'TS', (0, 1)],
    ['LR', 'TO', 'SIDE', (1, 0)],
    ['V', 'AND', 'VAND', (1, 0)]
]

# The functions that are used to interpret our logical forms with eval.
# They are imported into the namespace Grammar.sem to achieve that.
functions = {
    'identity': (lambda x: x),
    'exist': (lambda n: (lambda b: update_guess(b) and len(b) in n)),
    'und': (lambda v1: (lambda v2: v1 and v2)),
    'oder': (lambda v1: (lambda v2: v1 or v2)),
    'xoder': (lambda v1: (lambda v2: (v1 and not v2) or (v2 and not v1))),

    'blue': (lambda x: block_filter([(lambda b:b.colour == "blue")], x)),
    'red': (lambda x: block_filter([(lambda b:b.colour == "red")], x)),
    'green': (lambda x: block_filter([(lambda b:b.colour == "green")], x)),
    'yellow':(lambda x: block_filter([(lambda b:b.colour == "yellow")], x)),

    'under': (lambda n: (lambda x: (lambda y: position_test(y, x, n, "u")))),
    'over': (lambda n: (lambda x: (lambda y: position_test(y, x, n, "o")))),
    'next': (lambda n: (lambda x: (lambda y: position_test(y, x, n, "n")))),
    'left': (lambda n: (lambda x: (lambda y:position_test(y, x, n, "l")))),
    'right': (lambda n: (lambda x: (lambda y: position_test(y, x, n, "r"))))
}


# Main is used for testing the grammar with the test sentences from semdata.py
# Run the main for a simple demo of our grammar with respect to a

if __name__ == '__main__':

    from semdata import test_utterances
    from world import *

    # creates the grammar 
    gram = Grammar(gold_lexicon, rules, functions)

    # use picture from world.png and world.py for testing purpose
    allblocks2 = []
    all_blocks_grid = allblocks_test.copy()
    for row in allblocks_test:
        for blo in row:
            if blo:
                allblocks2.append(blo)
    allblocks = allblocks2

    # parses all test sentences from semdata.py
    # prints the derived logical forms for each test sentence and whether the test sentence is true with respect to the example picture world.png
    for i,u in enumerate(test_utterances):

        # creates the global variable for keeping track of which block is / blocks are the described one(s)
        guessed_blocks = set()
        
        lfs = gram.gen(u)
        if len(lfs) > 1:
            print("longer")
        print("======================================================================")
        print('Utterance: {}'.format(u))
        for lf in lfs:
            print("\tLF: {}".format(lf.formular))
            print('\tDenotation: {}'.format(lf.semantic))
            print(lf.guessed_blocks)

            # if utterance doesn't describe sentence not blocks should be guessed at all
            if lf.semantic == False:
                guessed_blocks = set()

            # visualization of how the computer gives feedback about what it "understood"
            # for the example for the sentence 'there is a red triangle under a blue square' the picture object corresponding to world.png is created
            # and a png file is created and saved where the blocks that are in all_blocks_grid are marked, e.g. all blocks that are red and have shape
            # triangle and are positioned below a blue square in the grid are marked as well as the blue squares that are above the red triangle
            
            from BlockPictureGenerator import * 
            test_pic = Picture(name = "./marked_pictures/" + u)
            test_pic.blocks = allblocks.copy()
            test_pic.block_n = len(test_pic.blocks)
            test_pic.grid = all_blocks_grid

            test_pic.draw()
            guess = []
            for b in lf.guessed_blocks:
                guess.append((b.y, b.x))
            test_pic.mark(guess)


                

    


