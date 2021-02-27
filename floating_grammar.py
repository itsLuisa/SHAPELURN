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
    :return: list containing all lists from gold lexicon with the (category, logical form) tuples
    """
    crude_rules = set()
    for key, value in gold_lexicon.items():
        for entry in value:
            crude_rules.add((entry[0], entry[1], 0))
        #crude_rules.add(value[0])

    return list(crude_rules)





class ParseItem:
    """
    :param categorie:
    """
    def __init__(self, categorie, length, semantic, components, str_form, guesses, weight, rem_words, incl_words):
        self.c = categorie
        self.s = length
        self.semantic = semantic
        self.components = components
        self.formular = str_form
        self.guessed_blocks = guesses
        self.summed_weights = weight
        self.rem_words = rem_words
        self.incl_words = incl_words


def check_preconditions(pi_1, pi_2):
    flag1 = False
    flag2 = False

    if len(pi_1.incl_words) <= len(pi_2.rem_words):
        flag1 = True
        temp_list = pi_2.rem_words.copy()
        for w in pi_1.incl_words:
            try:
                temp_list.remove(w)
            except:
                flag1 = False

    if len(pi_2.incl_words) <= len(pi_1.rem_words):
        flag2 = True
        temp_list = pi_1.rem_words.copy()
        for w in pi_2.incl_words:
            try:
                temp_list.remove(w)
            except:
                flag2 = False

    if flag1 and flag2:
        new_incl = pi_1.incl_words + pi_2.incl_words
        new_rem = pi_1.incl_words.copy() + pi_1.rem_words.copy()
        for w in new_incl:
            new_rem.remove(w)
        return new_incl, new_rem
    else:
        return None, None



class Grammar:

    def __init__(self, lexicon, rules, functions):
        """For examples of these arguments, see below."""
        self.lexicon = lexicon
        self.functions = functions
        self.rules = rules

    def gen(self,s):
        """ Floating Parser"""
        words = s.split()
        maxlen = len(words)+2
        chart = defaultdict(set)
        lex_agenda = []

        # construct predicates according to utterance
        for word in words:
            for categorie, function, weight in self.lexicon[word]:
                semantic = None
                remaining_words = words.copy()
                remaining_words.remove(word)
                item = ParseItem(categorie, 1, semantic, {(word, function)}, function, guessed_blocks, weight, remaining_words, [word])
                chart[categorie, 1].add(item)
                lex_agenda.append(item)


        # TODO: construct predicates out of the air
        # TODO: not really tested yet if this works correctly
        for (categorie, function, weight) in out_of_air:
            item = ParseItem(categorie, 1, None, {("", function)}, function, guessed_blocks, weight, words, [])
            lex_agenda.append(item)


        # construct longer formulas using this components:
        maxlen_currently = 1
        n_stucked = 0
        while (maxlen_currently <= maxlen):
            prev_agenda_len = len(lex_agenda)
            for item in lex_agenda:
                s1 = item.s
                c1 = item.c
                components1 = item.components
                new_items = set()

                for c2, s2 in chart:

                    s_new = s1+s2
                    if maxlen_currently < s_new:
                        maxlen_currently = s_new

                    if (c2,c1) in self.rules:
                        c_new = self.rules[c2, c1]
                        for item2 in chart[c2, s2]:

                            new_incl, new_rem = check_preconditions(item, item2)
                            if not new_incl:
                                continue
                            stucked = False
                            semantic_new = None
                            components_new = components1.union(item2.components)
                            function_new = item2.formular + "(" + item.formular + ")"
                            weight_new = item.summed_weights + item2.summed_weights
                            item_new = ParseItem(c_new, s_new, semantic_new, components_new, function_new, guessed_blocks,
                                                  weight_new, new_rem, new_incl)
                            if not self.check_member(lex_agenda, item_new):
                                lex_agenda.append(item_new)
                            new_items.add(item_new)

                    if (c1,c2) in self.rules:
                        c_new = self.rules[c1, c2]
                        for item2 in chart[c2, s2]:

                            new_incl, new_rem = check_preconditions(item, item2)
                            if not new_incl:
                                continue
                            stucked = False
                            semantic_new = None
                            components_new = components1.union(item2.components)
                            function_new = item.formular + "(" + item2.formular + ")"
                            weight_new = item.summed_weights + item2.summed_weights
                            item_new = ParseItem(c_new, s_new, semantic_new, components_new, function_new, guessed_blocks,
                                                  weight_new, new_rem, new_incl)
                            if not self.check_member(lex_agenda, item_new):
                                lex_agenda.append(item_new)
                            new_items.add(item_new)

                for new_item in new_items:
                    chart[new_item.c,new_item.s].add(new_item)

            # check whether parsing is stucked because not parse tree can be built
            stucked = len(lex_agenda) == prev_agenda_len
            if stucked:
                n_stucked += 1
            if n_stucked == 2:
                break

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


gold_lexicon = {
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
    'three':[('N','[3]', 1)],
    'under': [('POS', 'under', 1)],
    'over': [('POS', 'over', 1)],
    'next': [('POS', 'next', 1)],
    'left': [('POS', 'left', 1)],
    'right': [('POS', 'right', 1)],
    'and': [('CONJ', 'und', 1)],
    'or': [('CONJ', 'oder', 1),('CONJ','xoder', 1)],

}

out_of_air = [
    ('C', 'anycol', 1)
]



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




rules2 = {
 ('EN','B'): 'V',
 ('EN','BS'):'V',
 ('VAND','V'):'V',
 ('I','N'):'EN',
 ('E','I'):'I',
 ('C','B'):'B',
 ('L','B'):'BS',
 ('POS','B'):'L',
 ('POS','BS'):'L',
 ('PP','N'):'POS',
 ('TO','NEXT'):'PP',
 ('TS','SIDE'):'PP',
 ('TO','THE'):'TS',
 ('TO','LR'):'SIDE',
 ('AND','V'):'VAND'
}




functions2 = {
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

gold_lexicon2 = {
    'form':[('B', 'block_filter([], allblocks)', 1)],
    'forms':[('B', 'block_filter([], allblocks)', 1)],
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
    'there': [('E', 'identity', 1)],
    'is': [('I', 'exist', 1)],
    'are': [('I', 'exist', 1)],
    'a':[('N','range(1,17)', 1)],
    'one':[('N','[1]', 1)],
    'two':[('N','[2]', 1)],
    'three':[('N','[3]', 1)],
    'under': [('U', 'under', 1)],
    'over': [('U', 'over', 1)],
    'and': [('AND', 'und', 1)],
    'or': [('AND', 'oder', 1),('AND','xoder', 1)],
    'next': [('NEXT', 'next', 1)],
    'to': [('TO', 'identity', 1)],
    'of': [('TO', 'identity', 1)],
    'left': [('LR', 'left', 1)],
    'right': [('LR', 'right', 1)],
    'the': [('THE', 'identity', 1)]

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
    gram = Grammar(gold_lexicon, rules, functions)
    allblocks2 = []
    all_blocks_grid = allblocks_test.copy()
    for row in allblocks_test:
        for blo in row:
            if blo:
                allblocks2.append(blo)
    allblocks = allblocks2

    #lfs = gram.gen("is a red triangle over a blue triangle")
    #lfs = gram.gen("is one red triangle over a red triangle")
    #lfs = gram.gen("is a red triangle")
    lfs = gram.gen("is a triangle")
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
