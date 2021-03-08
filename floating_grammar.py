import sys
from collections import defaultdict
from itertools import product
from eval_helper import *
from world import *

"""
Defines our grammar: the lexicon (which is used without the keys in the game when learning from scratch), the CFG rules
and the functions on how to evaluate the logical forms with respect to a current Picture Object
It also includes the floating parser used to parse the input utterances and convert into logical forms

Terminology:
Difference between referenced and guessed blocks:
for sentences like "there is a red circle" both refer to the same Block objects, i.e. the objects of all red circles in the Picture
but for e.g. the sentence "there is a green triangle over a red square over a circle" referenced blocks consists of
all green triangles that are over red squares that are over any circle
whereas guessed blocks consists of all green triangles, red squares and circles that make this sentence true
"""

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
    :return: set containing all lists from gold lexicon with the (category, logical form) tuples
    """
    crude_rules = set()
    for key, value in gold_lexicon_basic.items():
        for entry in value:
            crude_rules.add((entry[0], entry[1], 0))

    return list(crude_rules)



class ParseItem:
    """
    Objects representing the logical formulas that the floating parser builds up step by step
    c: string, category of the formula
    s: int, size of the formula (= out of how many subformulas it is built)
    semantic: Truth value of the formula when evaluated with respect to a picture; None if the formula is not a complete
                formula, i.e. if c is not "V"
    components: set of pairs of words from the utterance and the lexical rule paired with it by the parser
    formular: string representation of the formula
    guessed_blocks: list of Block Objects, list of the guessed blocks when formular is evaluate w.r.t a given picture
                    the list is empty if formula is not complete yet, i.e. if c is not "V"
    summed_weights: float, sum of the weights of the subformulas
    """
    def __init__(self, categorie, length, semantic, components, str_form, guesses, weight):
        """
        :param categorie: string, category of the formula
        :param length: int, size of the formula
        :param semantic: Truth value of the formula or None
        :param components: set of pairs of words from the utterance and the lexical rule paired with it by the parser
        :param str_form: string representation of the formula
        :param guesses: list of Block Objects or empty list
        :param weight: float, weight of the formula
        """
        self.c = categorie
        self.s = length
        self.semantic = semantic
        self.components = components
        self.formular = str_form
        self.guessed_blocks = guesses
        self.summed_weights = weight

"""
The framework below is taken from Potts & Liang
We defined our own lexicon, rules and  functions and extended the main function demonstrating our grammar framework
The Grammar class was taken from Potts & Liang and we kept the sem function but replaced methods for the actual parsing
with an implementation of the floating parser instead of the basic cky parser
"""

class Grammar:

    def __init__(self, lexicon, rules, functions):
        """For examples of these arguments, see below."""
        self.lexicon = lexicon
        self.functions = functions
        self.rules = rules


    def extend_crude_lexicon(self, level):
        """
        extend the lexicon of the grammar by the lexical rules from gold_lexicon_extended according to current level
        :return:
        """
        extension = gold_lexicon_extended[level-2]
        for key, value in extension.items():
            for entry in value:
                self.lexicon.add((entry[0], entry[1], 0))


    def gen(self,s):
        """
        The Floating Parser
        :param s: string, the input utterance
        :return: a list of all ParseItems that correspond to all possible logical formulas of category "V" that can be
                generated for the input utterance based on the grammar
        """
        # tokens of the input utterance
        words = s.split()
        # maximum length until which parser should build up formulas
        # set to length of input + 2 to account for potentially missing color that has to be inserted "out of the air"
        maxlen = len(words)+2
        # initialize parse chart
        chart = defaultdict(set)
        # agenda with all ParseItems that the parser has not tried to combine to any entry in the parse chart so far
        agenda = []

        # construct predicates according to tokens in the utterance
        # constructs a ParseItem for each input token and each lexical rule matching it according to the lexicon
        for word in words:
            for categorie, function, weight in self.lexicon[word]:
                semantic = None
                item = ParseItem(categorie, 1, semantic, {(word, function)}, function, guessed_blocks, weight)
                chart[categorie, 1].add(item)
                agenda.append(item)

        # constructs predicates out of the air (i.e. with no corresponding token in the input utterance)
        for (categorie, function, weight) in out_of_air:
            item = ParseItem(categorie, 1, None, {("", function)}, function, guessed_blocks, weight)
            agenda.append(item)

        # construct longer formulas bottom-up by combining the shorter ones based on the rules of the grammar:
        maxlen_currently = 1
        # build up all possible formulas until no formula not exceeding the max. length is left
        while agenda:
            # take a not yet considered formula from the agenda
            item = agenda.pop(0)
            s1 = item.s
            c1 = item.c
            components1 = item.components
            new_items = set()

            # try if this formula can be combined with any other formula in the parse chart to yield a
            # new, longer formula in line with the grammar
            for c2, s2 in chart:
                s_new = s1+s2
                if maxlen_currently < s_new:
                    maxlen_currently = s_new

                if (c2,c1) in self.rules:
                     c_new = self.rules[c2, c1]
                     # for each possible combination create a new ParseItem object for the resulting combined formula
                     for item2 in chart[c2, s2]:
                         semantic_new = None
                         components_new = components1.union(item2.components)
                         function_new = item2.formular + "(" + item.formular + ")"
                         weight_new = item.summed_weights + item2.summed_weights
                         item_new = ParseItem(c_new, s_new, semantic_new, components_new, function_new, guessed_blocks,
                                              weight_new)
                         # only add new ParseItem if its formula does not exceed the max size
                         if s_new <= maxlen:
                            # check that new ParseItem is not already on the agenda
                            if not self.check_member(agenda, item_new):
                                agenda.append(item_new)
                         
                            new_items.add(item_new)

                if (c1,c2) in self.rules:
                     c_new = self.rules[c1, c2]
                     # for each possible combination create a new ParseItem object for the resulting combined formula
                     for item2 in chart[c2, s2]:
                         semantic_new = None
                         components_new = components1.union(item2.components)
                         function_new = item.formular + "(" + item2.formular + ")"
                         weight_new = item.summed_weights + item2.summed_weights
                         item_new = ParseItem(c_new, s_new, semantic_new, components_new, function_new, guessed_blocks,
                                              weight_new)
                         # only add new ParseItem if its formula does not exceed the max size
                         if s_new <= maxlen:
                            # check that new ParseItem is not already on the agenda
                            if not self.check_member(agenda, item_new):
                                agenda.append(item_new)
                         
                            new_items.add(item_new)

            # add the newly built ParseItems to the chart
            for new_item in new_items:
                # check that only ParseItems that are not already in the chart are added
                chart_list = list(chart[new_item.c, new_item.s].copy())
                if not self.check_member(chart_list, new_item):
                    chart[new_item.c,new_item.s].add(new_item)

        results = []
        # keep track that ParseItems that represent the same formula built from the same components only occur once in the result
        included_items = []
        # out of all the formulas the parse built up, only return those that are complete, i.e. category = "V" and can
        # be evaluated
        for (c,s) in chart:
            if c == 'V':
                for item in chart[c,s]:
                    # evaluate the formula
                    item.semantic = self.sem(item)
                    # store the guessed_blocks that were created during evaluation and reset for next formula
                    item.guessed_blocks = guessed_blocks.copy()
                    guessed_blocks.clear()
                    # if average of weights should be computed for the total weight of a formula include the line below
                    # item.summed_weights = item.summed_weights / item.s
                    if self.check_member(included_items, item):
                        continue
                    else:
                        results.append(item)
                        included_items.append(item)

        return results


    def check_member(self, p_item_list, p_item):
        """
        checks for an ParseItem and a list of ParseItems whether there is already a ParseItem with the same formular and the same components in the list
        :param p_item_list: a list of ParseItem objects
        :param p_item: a ParseItem object
        :return: True or False
        """
        for pi in p_item_list:
            if pi.formular == p_item.formular and pi.components == p_item.components:
                return True
        return False


    def sem(self, lf):
        """Interpret, as Python code, the root of a logical form
        generated by this grammar."""
        # Import all of the user's functions into the namespace to
        # help with the interpretation of the logical forms.
        grammar = sys.modules[__name__]
        for key, val in list(self.functions.items()):
            setattr(grammar, key, val)
        # Interpret semantics.
        return eval(lf.formular)


# The lexica for our pictures
# Lexica map strings to list of tuples of (category, logical form)
# gold_lexicon_basic consists of the basic lexical rules needed from first level on
gold_lexicon_basic = {
    'form':[('B', 'block_filter([], allblocks)', 1)],
    'forms':[('B', 'block_filter([], allblocks)')],
    'square': [('B', 'block_filter([lambda b: b.shape=="rectangle"],allblocks)', 1)],
    'squares': [('B', 'block_filter([lambda b: b.shape=="rectangle"], allblocks)', 1)],
    'triangle': [('B', 'block_filter([(lambda b: b.shape == "triangle")], allblocks)', 1)],
    'triangles': [('B', 'block_filter([(lambda b: b.shape == "triangle")], allblocks)', 1)],
    'circle': [('B', 'block_filter([(lambda b: b.shape == "circle")], allblocks)', 1)],
    'circles': [('B', 'block_filter([(lambda b: b.shape == "circle")], allblocks)', 1)],
    'is': [('E', 'exist', 1)],
    'are': [('E', 'exist', 1)],
    'a':[('N','range(1,17)', 1)],
    'one':[('N','[1]', 1)],
    'two':[('N','[2]', 1)],
    'three':[('N','[3]', 1)]

}

# # gold_lexicon_extended consists of the lexical rules not needed in level 1 but later on
# first dictionary for level 2, second dictionary for level 3
gold_lexicon_extended = [
    {
        'green': [('C', 'green', 1)],
        'yellow': [('C', 'yellow', 1)],
        'blue': [('C', 'blue', 1)],
        'red': [('C', 'red', 1)]
    },
    {
        'under': [('POS', 'under', 1)],
        'over': [('POS', 'over', 1)],
        'next': [('POS', 'next', 1)],
        'left': [('POS', 'left', 1)],
        'right': [('POS', 'right', 1)],
        'and': [('CONJ', 'und', 1)],
        'or': [('CONJ', 'oder', 1), ('CONJ', 'xoder', 1)]
    }
]

# lexical rules that can be used to add a logical formula not corresponding to a word in the input utterance
out_of_air = {
    ('C', 'anycol', 1)
}

# The binarized rule dictionary for our pictures, start symbol is V
# each entry has a pair of categories as key and a category as value, ('B', 'C') : 'A'
# where A is the parent category, B the left child and C the right child
# order of the child categories defines the order in which the logical representations are applied
# e.g. The first rule corresponds to: V -> EN  BC  and specifies that EN is applied to BC: EN(BC)
rules = {
 ('EN', 'BC'): 'V',
 ('EN', 'BS'): 'V',
 ('CONJ', 'V'): 'CONJ_1',
 ('CONJ_1', 'V'): 'V',
 ('E', 'N'): 'EN',
 ('C', 'B'): 'BC',
 ('POS', 'N'): 'POS_N',
 ('POS_N', 'BC'): 'POS_NB',
 ('POS_NB', 'BC'): 'BC',
 ('POS_NB', 'BC'): 'BS'

}

# The functions that are used to interpret our logical forms with eval.
# They are imported into the namespace Grammar.sem to achieve that.
functions = {
    'exist': (lambda n: (lambda b: update_guess(b) and len(b) in n)),
    'und': (lambda v1: (lambda v2: v1 and v2)),
    'oder': (lambda v1: (lambda v2: v1 or v2)),
    'xoder': (lambda v1: (lambda v2: (v1 and not v2) or (v2 and not v1))),

    'blue': (lambda x: block_filter([(lambda b:b.colour == "blue")], x)),
    'red': (lambda x: block_filter([(lambda b:b.colour == "red")], x)),
    'green': (lambda x: block_filter([(lambda b:b.colour == "green")], x)),
    'yellow':(lambda x: block_filter([(lambda b:b.colour == "yellow")], x)),
    'anycol':(lambda x: block_filter([], x)),

    'under': (lambda n: (lambda x: (lambda y: position_test(y, x, n, "u")))),
    'over': (lambda n: (lambda x: (lambda y: position_test(y, x, n, "o")))),
    'next': (lambda n: (lambda x: (lambda y: position_test(y, x, n, "n")))),
    'left': (lambda n: (lambda x: (lambda y:position_test(y, x, n, "l")))),
    'right': (lambda n: (lambda x: (lambda y: position_test(y, x, n, "r"))))
}



def grouping(lfs):
    groups = defaultdict(list)
    max_weights = []
    for lf in lfs:
        if lf.semantic:
            groups[frozenset(lf.guessed_blocks)].append(lf)
    #print(groups)
    for grouped_items in groups.values():
        grouped_items.sort(key=lambda p_item: p_item.summed_weights, reverse=True)
    #print(groups)

    for gue_bl, grouped_items in groups.items():
        max_weights.append((gue_bl, grouped_items[0].summed_weights))

    max_weights.sort(key=lambda  tuple: tuple[1], reverse=True)
    sorted_guesses = [gue_bl for (gue_bl, weight) in max_weights]

    return groups, sorted_guesses


if __name__ == "__main__":
    #creat_all_blocks(setPicParameters())
    gold_lexicon = gold_lexicon_basic.copy()
    gold_lexicon.update(gold_lexicon_extended,2)
    gold_lexicon.update(gold_lexicon_extended,3)
    gram = Grammar(gold_lexicon, rules, functions)
    allblocks2 = []
    all_blocks_grid = allblocks_test.copy()
    for row in allblocks_test:
        for blo in row:
            if blo:
                allblocks2.append(blo)
    allblocks = allblocks2

    #lfs = gram.gen("is a red triangle over a blue triangle")
    #lfs = gram.gen("is one red triangle over a blue triangle")
    #lfs = gram.gen("is a red triangle")
    lfs = gram.gen("is a red triangle and a red triangle")
    for lf in lfs:
        print(lf.c,lf.s,lf.semantic,lf.components)
        print(lf.formular)
        print(lf.guessed_blocks)
        print("weight: " + str(lf.summed_weights))
        print("\n")
    print("GROUPING")
    g = grouping(lfs)
    print(g[0])
    print(g[1])

