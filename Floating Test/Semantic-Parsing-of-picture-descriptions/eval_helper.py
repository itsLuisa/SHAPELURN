"""
This file defines the methods used in the functions of the grammar in grammar.py
They are used to find the blocks in the Picture object described in the input utterance
"""


def position_test(blocks, block_locations, number, position):
    """
    finds all pairs of blocks b1 and b2 from blocks and block_locations respectively
    that stand in relation position to eachother and checks if number of blocks is true
    e.g. blocks is a list of all blue rectangles and block_locations a list of all red circles, number is 2, position is 'u'
    then the function returns the list of all blocks that are blue rectangles and are below 2 red circles and updates the
    back_track attribute of each of those blue rectangles by adding the red circles that make the description true w.r.t
    the specific blue rectangle
    :param blocks: list of blocks are the referenced block
    :param block_locations: list of blocks are the referenced blocks
    :param number: the number of blocks from block_locations that should fulfill the relation
    :param position: string for the relative position
    :return: list of all blocks from blocks that stand in relation position to any block in block_locations
    """
    ref_blocks1 = blocks
    ref_blocks2 = block_locations

    fulfill_ref = set()

    matching_combs = []

    for b1 in ref_blocks1:
        matching_b2 = set()

        for b2 in ref_blocks2:

            match = False
            if position == "u" and b1.y > b2.y:
                match = True

            elif position == "o" and b1.y < b2.y:
                match = True

            elif position == "n":
                if b1.y == b2.y and (not b1.x == b2.x):
                    match = True

            elif position == "l" and b1.x < b2.x:
                match = True

            elif position == "r" and b1.x > b2.x:
                match = True

            if match == True:
                matching_b2.add(b2)
                b1.keep_track(b2)

        if matching_b2 != []:
            matching_combs.append((b1,matching_b2))

    for b1,b2s in matching_combs:
        if len(b2s) in number:
            fulfill_ref.add(b1)

    fulfill_ref = list(fulfill_ref)

    return fulfill_ref


def block_filter(conditions, blocks):
    """
    checks which blocks match a certain condition such as shape == rectangle or color == green
    :param conditions: list of conditions
    :param blocks: list of blocks are the referenced blocks
    :return: list of referenced blocks fulfilling the conditions
    """
    fulfill_ref = []

    for b in blocks:
        test = True
        for c in conditions:
            if not c(b):
                test = False
        if test:
            fulfill_ref.append(b)

    return fulfill_ref