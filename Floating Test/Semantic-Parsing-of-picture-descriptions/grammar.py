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
    def __init__(self,categorie,length,semantic,components,str_form):
        self.c = categorie
        self.s = length
        self.semantic = semantic
        self.components = components
        self.formular = str_form



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
        agenda = []
        # construct predicates according to utterance
        for word in words:
            for categorie,function in self.lexicon[word]:
                try:
                    semantic = self.functions[function]
                except:
                    semantic = eval(function)
                item = ParseItem(categorie,1,semantic,{(word,function)}, function)
                chart[categorie,1].add(item)
                agenda.append(item)
        # TODO: construct predicates out of the air 
        for function in functions:
            pass
        # construct longer formulas using this components:
        maxlen_currently = 1
        while (maxlen_currently <= maxlen) and agenda :
            item = agenda.pop(0)
            s1 = item.s
            c1 = item.c
            components1 = item.components
            semantic1 = item.semantic
            new_items = set()
            for c2,s2 in chart:
                #s_new = 1+s1+s2
                s_new = s1+s2
                if maxlen_currently < s_new:
                    maxlen_currently = s_new
                if (c2,c1) in self.rules:
                     c_new = self.rules[c2,c1]
                     for item2 in chart[c2,s2]:
                         #print(semantic1,item2.semantic,c1,item2.c)
                         semantic_new = item2.semantic (semantic1)
                         #print(semantic_new)
                         components_new = components1.union(item2.components)
                         function_new = item2.formular + "(" + item.formular + ")"
                         item_new = ParseItem(c_new,s_new,semantic_new,components_new,function_new)
                         agenda.append(item_new)
                         new_items.add(item_new)
                if (c1,c2) in self.rules:
                     c_new = self.rules[c1,c2]
                     for item2 in chart[c2,s2]:
                         semantic_new = semantic1 (item2.semantic)
                         components_new = components1.union(item2.components)
                         function_new = item.formular + "(" + item2.formular + ")"
                         item_new = ParseItem(c_new,s_new,semantic_new,components_new,function_new)
                         agenda.append(item_new)
                         new_items.add(item_new)
            for new_item in new_items:
                chart[new_item.c,new_item.s].add(new_item)

        results = []
        included_items = []
        for (c,s) in chart:
            if c =='V':
                for item in chart[c,s]:
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
        #return eval(lf[0][1])  # Interpret just the root node's semantics.
        return eval(lf.formular)
            
                
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
    'is': [('E', 'exist')],
    'are': [('E', 'exist')],
    'a':[('N','range(1,17)')],
    'one':[('N','[1]')],
    'two':[('N','[2]')],
    'three':[('N','[3]')],
    'under': [('POS', 'under')],
    'over': [('POS', 'over')],
    'next': [('POS', 'next')],
    'left': [('POS', 'left')],
    'right': [('POS', 'right')],
    'and': [('CONJ', 'und')],
    'or': [('CONJ', 'oder'),('CONJ','xoder')],
    'epsilon': [('C', 'anycol')]

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





from world import *
#creat_all_blocks(setPicParameters())
gram = Grammar(gold_lexicon, rules, functions)
allblocks2 = []
all_blocks_grid = allblocks_test.copy()
for row in allblocks_test:
    for blo in row:
        if blo:
            allblocks2.append(blo)
allblocks = allblocks2

lfs = gram.gen("epsilon is one yellow triangle")
for lf in lfs:
    print(lf.c,lf.s,lf.semantic,lf.components)
    print(lf.formular)
    print(gram.sem(lf))
    
