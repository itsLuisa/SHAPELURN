"""
only used for demonstration of grammar.py
creates a list of blocks corresponding to the picture world2.png
"""

class Block:
    """
    Object Block has attributes colour and x and y coordinate and shape (can be circle, triangle or rectangle)
    """
    def __init__(self, colour, shape):
        """
        Block object only initialized with colour, coordinates are set separately
        :param colour: a colour as specified in the list colours
        """
        self.colour = colour
        self.shape = shape
        self.x = None
        self.y = None
        self.back_track = []

    def set_coordinates(self, x, y):
        """
        sets the coordinates of the block w.r.t. the position in the grid, upper left corner has coordinates (0,0)
        :param x: column index
        :param y: row index
        :return:
        """
        self.x = x
        self.y = y

    def __str__(self):
        """
        creates a readable string reprsentation of a Block object
        """
        s = self.shape + ": " + self.colour
        return s

    def keep_track(self, block):
        self.back_track.append(block)


def set_all_coordinates(chart):
    for row in range(1,len(chart)+1):
        for column in range(1,len(chart[row-1])+1):
            if chart[row-1][column-1] != None:
                chart[row-1][column-1].set_coordinates(column,row)
                
    

# for the simple world.png picture
one = Block("blue","rectangle")
two = Block("blue","rectangle")
three = Block("blue","triangle")
four = Block("yellow","rectangle")
five = Block("red","triangle")

world = [[None,one,two,None],[three,None,None,four],[None,five,None,None],[None,None,None,None]]

# for the world2.png picture
one = Block("red","triangle")
two = Block("blue","circle")
three = Block("red","circle")
four = Block("yellow","circle")
five = Block("yellow","triangle")
six = Block("blue","circle")
seven = Block("yellow","circle")
eight = Block("blue","circle")
nine = Block("red","circle")
ten = Block("green","circle")
eleven = Block("green","triangle")
twelve = Block("red","triangle")
thirteen = Block("green","rectangle")
fourteen = Block("green","circle")
fivteen = Block("yellow","circle")
sixteen = Block("blue","triangle")

world2 = [[one,two,three,four],[five,six,seven,eight],[nine,ten,eleven,twelve],[thirteen,fourteen,fivteen,sixteen]]


# choose which example picture you would like to use
# allblocks_test = world
allblocks_test = world
set_all_coordinates(allblocks_test)



