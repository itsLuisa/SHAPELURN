import unittest
from grammar import *
from world import *
from BlockPictureGenerator import *

"""
unit tests for debugging and testing that the guessed blocks are generated correctly
uses world2.py and world2.jpg as test picture
"""

gram = Grammar(gold_lexicon, rules, functions)

# use picture from world.png and world.py for testing purpose
allblocks2 = []
all_blocks_grid = allblocks_test.copy()
for row in allblocks_test:
    for blo in row:
        if blo:
            allblocks2.append(blo)
allblocks = allblocks2
test_pic = Picture(name = "./marked_pictures/world")
test_pic.blocks = allblocks.copy()
test_pic.block_n = len(test_pic.blocks)
test_pic.grid = all_blocks_grid
create_all_blocks(test_pic)


test_set = [
    ('there is a square', True, {(4,1)}),
    ('there are three blue circles', True, {(1,2),(2,2),(2,4)}),
    ('there are two red triangles', True, {(1,1), (3,4)}),
    ('there is a green square', True, {(4,1)}),
    ('there is a yellow triangle', True, {(2,1)}),
    ('there is a yellow form', True, {(1,4),(2,1),(2,3),(4,3)})
]
test_sentences_conj = [
    ('there is a yellow triangle and there is a green square', True, {(2,1),(4,1)}),
    ('there is a yellow triangle and there is a yellow circle', True, {(2,1),(1,4),(2,3),(4,3)}),
    ('there is a yellow triangle and there is a red triangle', True, {(1,1),(2,1), (3,4)})
]

test_sentences_pos = [
    ('there is a green circle over a green circle', True, {(3,2),(4,2)}),
    ('there is a green triangle under a red circle', True, {(3,3),(1,3)}),
    ('there is a green circle to the right of a red circle', True, {(3,1),(3,2),(4,2)}),
    ('there is a green form next to a green form', True, {(3,2),(3,3),(4,1),(4,2)}),
    ('there is a blue circle under a blue circle', True, {(1,2),(2,2),(2,4)}),
    ('there is a yellow circle over a blue circle', True, {(1,4),(2,2),(2,4)}),
    ('there is a red triangle over a yellow triangle', True, {(1,1),(2,1)}),
    ('there is a yellow triangle under a red triangle', True, {(1,1),(2,1)}),
    ('there is a red triangle under a yellow triangle', True, {(2,1),(3,4)}),
    ('there is a yellow triangle over a red triangle', True, {(2,1),(3,4)}),
    ('there are two green circles under three blue circles', True, {(1,2),(2,2),(2,4),(3,2),(4,2)}),
    ('there are two green circles under two blue circles', False, set()),
    ('there are two green circles under a blue circle', True, {(1,2),(2,2),(2,4),(3,2),(4,2)}),
    ('there is a blue circle over two yellow circles', True, {(1,2),(2,3),(4,3)}),
    ('there is a blue circle over one yellow circle', True, {(2,2),(2,4),(4,3)}),
    ('there is a blue circle over a yellow circle', True, {(1,2),(2,2),(2,3),(2,4),(4,3)}),

    ('there is a red circle to the left of two circles', True, {(1, 3), (1, 4),(2, 4)}),
    ('there is a blue circle to the left of three yellow circles', True, {(1, 2), (1, 4), (2, 2), (2, 3),(4,3)}),
    ('there is a blue circle to the left of two yellow circles', False, set()),
    ('there is a blue circle to the left of three circles', False, set())
]

nested_test_sentences = [
('there is a blue triangle under a red triangle under a yellow triangle', True, {(2,1),(3,4),(4,4)}),
('there are two green circles under one yellow circle under a red circles', True, {(3,2),(4,2),(2,3),(1,3)})
]

special_sentences = [
    ('there is a green square under two triangles under two yellow circles', True, {(4,1),(3,3),(3,4),(2,3),(1,4)}),
    ('there is a red triangle next to a blue circle next to a red circle next to a yellow circle', True, {(1,1),(1,2),(1,3),(1,4)}),
    ('there is a yellow circle to the left of a blue circle to the right of yellow triangle', True, {(2,3),(3,4),(2,1)}),
    ('there is a red circle next to a circle next to two triangles', True, {(3,1),(3,2),(3,3),(3,4)}),
    ('there is a green square next to a yellow circle next to a green circle', True, {(4,1),(4,2),(4,3)}),
    ('there is a green square next to a green circle next to a red triangle', False, set()),
    ('there is a green square next to a green square', False, set()),
]

class MyTestCase(unittest.TestCase):
    def test_truth_simple(self):
        for test_ins in test_set:
            u = test_ins[0]
            print(u)
            t = test_ins[1]
            g = test_ins[2]

            lfs = gram.gen(u)
            for lf in lfs:
                seman = gram.sem(lf)
                guess = []
                for b in guessed_blocks:
                    guess.append((b.y, b.x))
                guessed_blocks.clear()

                self.assertEqual(t, seman)
                self.assertEqual(g, set(guess))

    def test_conjunction(self):
        for test_ins in test_sentences_conj:
            u = test_ins[0]
            print(u)
            t = test_ins[1]
            g = test_ins[2]

            lfs = gram.gen(u)
            for lf in lfs:
                seman = gram.sem(lf)
                guess = []
                for b in guessed_blocks:
                    guess.append((b.y, b.x))
                guessed_blocks.clear()

                self.assertEqual(t, seman)
                self.assertEqual(g, set(guess))

    def test_position(self):
        for test_ins in test_sentences_pos:
            u = test_ins[0]
            print(u)
            t = test_ins[1]
            g = test_ins[2]

            lfs = gram.gen(u)
            for lf in lfs:
                seman = gram.sem(lf)
                guess = []
                for b in guessed_blocks:
                    guess.append((b.y, b.x))
                guessed_blocks.clear()

                self.assertEqual(t, seman)
                self.assertEqual(g, set(guess))

    def test_nested(self):
        for test_ins in nested_test_sentences:
            u = test_ins[0]
            print(u)
            t = test_ins[1]
            g = test_ins[2]

            lfs = gram.gen(u)
            for lf in lfs:
                seman = gram.sem(lf)
                guess = []
                for b in guessed_blocks:
                    guess.append((b.y, b.x))
                guessed_blocks.clear()

                self.assertEqual(t, seman)
                self.assertEqual(g, set(guess))

    def test_special_cases(self):
        for test_ins in special_sentences:
            u = test_ins[0]
            print(u)
            t = test_ins[1]
            g = test_ins[2]

            lfs = gram.gen(u)
            for lf in lfs:
                seman = gram.sem(lf)
                guess = []
                for b in guessed_blocks:
                    guess.append((b.y, b.x))
                guessed_blocks.clear()

                self.assertEqual(t, seman)
                self.assertEqual(g, set(guess))


if __name__ == '__main__':
    unittest.main()
