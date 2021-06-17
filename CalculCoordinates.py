"""
This script contains an optional function to customize the size of the pictures and to
calculate the coordinates for the fields in the grids appropriately
"""

def calculate_coordinates(size_pic, size_grid, n, rel_blocks):
    """
    calcuates the coordinates of the upper left corner and the lower right corner of equally distributed
    blocks in a grid as needed for drawing with tkinter
    only works for square pictures and grids
    :param picture_size: size of one side of the square picture
    :param grid_size: size of one side of the square grid
    :param n: number of possible blocks per column and per row -> nxn grid
    :param rel_blocks: number between 0 and 1 specifying how much of the are of the grid is used for blocks
    :return: a dictionary with the coordinates
    """
    edge = (size_pic - size_grid) / 2           # distance between edge of picture and edge of the grid
    size_all_blocks = rel_blocks * size_grid    # how much of the area of the grid will be for the blocks
    space = size_grid - size_all_blocks         # and how much for space between them
    size_block = size_all_blocks / n            # length of the side of a block
    distance = space / (n+1)                    # distance between two blocks or a block and the edge of the grid
    dist_corners = distance + size_block        # distance between the two upper left corners of two blocks which are directly one next to the other or below each other

    xl_1cl = distance + edge                    # x-coordinate of the upper left corner of each block in the first column
    xr_1cl = distance + size_block + edge       # x-coordinate of the lower right corner of each block in the first column
    xl_2cl = xl_1cl + dist_corners              # x-coordinate of the upper left corner of each block in the second column
    xr_2cl = xr_1cl + dist_corners              # ...
    xl_3cl = xl_2cl + dist_corners
    xr_3cl = xr_2cl + dist_corners
    xl_4cl = xl_3cl + dist_corners
    xr_4cl = xr_3cl + dist_corners

    yl_1row = distance + edge                     # y-coordinate of the upper left corner of each block in the first row
    yr_1row = distance + size_block + edge        # y-coordinate of the lower right corner of each block in the first row
    yl_2row = yl_1row + dist_corners
    yr_2row = yr_1row + dist_corners
    yl_3row = yl_2row + dist_corners
    yr_3row = yr_2row + dist_corners
    yl_4row = yl_3row + dist_corners
    yr_4row = yr_3row + dist_corners

    row1 = {}
    row2 = {}
    row3 = {}
    row4 = {}
    row1[1] = ([(xl_1cl,yl_1row),(xr_1cl,yr_1row)])
    row1[2] = ([(xl_2cl,yl_1row),(xr_2cl,yr_1row)])
    row1[3] = ([(xl_3cl,yl_1row),(xr_3cl,yr_1row)])
    row1[4] = ([(xl_4cl,yl_1row),(xr_4cl,yr_1row)])
    row2[1] = ([(xl_1cl,yl_2row),(xr_1cl,yr_2row)])
    row2[2] = ([(xl_2cl,yl_2row),(xr_2cl,yr_2row)])
    row2[3] = ([(xl_3cl,yl_2row),(xr_3cl,yr_2row)])
    row2[4] = ([(xl_4cl,yl_2row),(xr_4cl,yr_2row)])
    row3[1] = ([(xl_1cl,yl_3row),(xr_1cl,yr_3row)])
    row3[2] = ([(xl_2cl,yl_3row),(xr_2cl,yr_3row)])
    row3[3] = ([(xl_3cl,yl_3row),(xr_3cl,yr_3row)])
    row3[4] = ([(xl_4cl,yl_3row),(xr_4cl,yr_3row)])
    row4[1] = ([(xl_1cl,yl_4row),(xr_1cl,yr_4row)])
    row4[2] = ([(xl_2cl,yl_4row),(xr_2cl,yr_4row)])
    row4[3] = ([(xl_3cl,yl_4row),(xr_3cl,yr_4row)])
    row4[4] = ([(xl_4cl,yl_4row),(xr_4cl,yr_4row)])

    coor = {}
    coor[1] = row1
    coor[2] = row2
    coor[3] = row3
    coor[4] = row4

    return coor
