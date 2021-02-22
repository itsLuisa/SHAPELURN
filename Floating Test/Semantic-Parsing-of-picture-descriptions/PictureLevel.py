from BlockPictureGenerator import *

"""
Allows to create a picture object as specified in BlockPictureGenerator with parameters based on the
current level and the current session
"""

def setPicParameters(level, i_picture, session_name):
    """
    creates a Picture object where the number of shown blocks is based on the current level
    returns the picture object after storing it in the subfolder session_name and giving it a unique file name
    :param level: numer (int) of the current level
    :param i_picture: number (int) of the current picture in the current level
    :param session_name: name of the current session
    :return: the Picture Object
    """

    file_name = session_name + "_L" + str(level) + "_" + str(i_picture)
    path_pict = "./" + session_name + "/" + file_name
    
    if level == 1:
        complexity = (3,4)

    elif level == 2:
        complexity = (3,4)
        
    elif level == 3:
        complexity = (3, 9)

    elif level == 4:
        complexity = (5, 13)

    else:
        complexity = (3,13)

    current_picture = Picture(complexity, path_pict)
    
    return current_picture



if __name__=="__main__":
    # for demonstrattion (only works if there exits a folder with name pictures in the source directory)
    test_picture = setPicParameters(1, 1, "pictures")
    test_picture.draw()


