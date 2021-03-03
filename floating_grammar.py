import sys
from collections import defaultdict
from itertools import product
from eval_helper import *
from world import *

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
        #crude_rules.add(value[0])

    return list(crude_rules)



class ParseItem:
    """
    :param categorie:
    """
    def __init__(self, categorie, length, semantic, components, str_form, guesses, weight):
        self.c = categorie
        self.s = length
        self.semantic = semantic
        self.components = components
        self.formular = str_form
        self.guessed_blocks = guesses
        self.summed_weights = weight



class Grammar:

    def __init__(self, lexicon, rules, functions):
        """For examples of these arguments, see below."""
        self.lexicon = lexicon
        self.functions = functions
        self.rules = rules


    def extend_crude_lexicon(self):
        """
        :return:
        """
        for key, value in gold_lexicon_extended.items():
            for entry in value:
                self.lexicon.add((entry[0], entry[1], 0))


    def gen(self,s):
        """ Floating Parser"""
        words = s.split()
        maxlen = len(words)+2
        print(maxlen)
        chart = defaultdict(set)
        agenda = []

        # construct predicates according to utterance
        for word in words:
            for categorie, function, weight in self.lexicon[word]:
                semantic = None
                item = ParseItem(categorie, 1, semantic, {(word, function)}, function, guessed_blocks, weight)
                chart[categorie, 1].add(item)
                agenda.append(item)

        # constructs predicates out of the air
        # TODO: not really tested yet if this works correctly in combination with the gui
        for (categorie, function, weight) in out_of_air:
            item = ParseItem(categorie, 1, None, {("", function)}, function, guessed_blocks, weight)
            agenda.append(item)

        # construct longer formulas using this components:
        maxlen_currently = 1
        #while (maxlen_currently <= maxlen) and agenda:
        while agenda:
            item = agenda.pop(0)
            s1 = item.s
            c1 = item.c
            components1 = item.components
            new_items = set()

            for c2, s2 in chart:
                s_new = s1+s2
                print(s_new)
                print(maxlen_currently)
                if maxlen_currently < s_new:
                    maxlen_currently = s_new

                if (c2,c1) in self.rules:
                     c_new = self.rules[c2, c1]
                     for item2 in chart[c2, s2]:
                         semantic_new = None
                         components_new = components1.union(item2.components)
                         function_new = item2.formular + "(" + item.formular + ")"
                         weight_new = item.summed_weights + item2.summed_weights
                         item_new = ParseItem(c_new, s_new, semantic_new, components_new, function_new, guessed_blocks,
                                              weight_new)

                         if s_new <= maxlen:
                            # check that new ParseItem is not already on the agenda
                            if not self.check_member(agenda, item_new):
                                agenda.append(item_new)
                         
                            new_items.add(item_new)

                if (c1,c2) in self.rules:
                     c_new = self.rules[c1, c2]
                     for item2 in chart[c2, s2]:
                         semantic_new = None
                         components_new = components1.union(item2.components)
                         function_new = item.formular + "(" + item2.formular + ")"
                         weight_new = item.summed_weights + item2.summed_weights
                         item_new = ParseItem(c_new, s_new, semantic_new, components_new, function_new, guessed_blocks,
                                              weight_new)
                         if s_new <= maxlen:
                            # check that new ParseItem is not already on the agenda
                            if not self.check_member(agenda, item_new):
                                agenda.append(item_new)
                         
                            new_items.add(item_new)

            #print("ITEM " + item.formular)
            for new_item in new_items:
                # check that only ParseItems that are not already in the chart are added
                #print(new_item.formular)
                chart_list = list(chart[new_item.c, new_item.s].copy())
                if not self.check_member(chart_list, new_item):
                    chart[new_item.c,new_item.s].add(new_item)

        results = []
        included_items = []
        for (c,s) in chart:
            if c == 'V':
                for item in chart[c,s]:
                    item.semantic = self.sem(item)
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


gold_lexicon_basic = {
    'form':[('B', 'block_filter([], allblocks)', 1)],
    'forms':[('B', 'block_filter([], allblocks)')],
    'square': [('B', 'block_filter([lambda b: b.shape=="rectangle"],allblocks)', 1)],
    'squares': [('B', 'block_filter([lambda b: b.shape=="rectangle"], allblocks)', 1)],
    'triangle': [('B', 'block_filter([(lambda b: b.shape == "triangle")], allblocks)', 1)],
    'triangles': [('B', 'block_filter([(lambda b: b.shape == "triangle")], allblocks)', 1)],
    'circle': [('B', 'block_filter([(lambda b: b.shape == "circle")], allblocks)', 1)],
    'circles': [('B', 'block_filter([(lambda b: b.shape == "circle")], allblocks)', 1)],
    'green': [('C', 'green', 1)],
    'yellow': [('C', 'yellow', 1)],
    'blue': [('C', 'blue', 1)],
    'red': [('C', 'red', 1)],
    'is': [('E', 'exist', 1)],
    'are': [('E', 'exist', 1)],
    'a':[('N','range(1,17)', 1)],
    'one':[('N','[1]', 1)],
    'two':[('N','[2]', 1)],
    'three':[('N','[3]', 1)]

}

gold_lexicon_extended = {
    'under': [('POS', 'under', 1)],
    'over': [('POS', 'over', 1)],
    'next': [('POS', 'next', 1)],
    'left': [('POS', 'left', 1)],
    'right': [('POS', 'right', 1)],
    'and': [('CONJ', 'und', 1)],
    'or': [('CONJ', 'oder', 1), ('CONJ', 'xoder', 1)]
}

out_of_air = {
    ('C', 'anycol', 1)
}

rules = {
 ('EN','BC'):'V',
 ('EN','BS'):'V',
 ('CONJ','V'):'CONJ_1',
 ('CONJ_1','V'):'V',
 ('E','N'):'EN',
 ('C','B'):'BC',
 ('POS','N'):'POS_N',
 ('POS_N','BC'):'POS_NB',
 ('POS_NB','BC'):'BC',
 ('POS_NB','BC'):'BS',

}



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
    gold_lexicon.update(gold_lexicon_extended)
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

