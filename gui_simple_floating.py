# imports
import PySimpleGUI as sg
import os, math
from gui_design import *
from BlockPictureGenerator import Picture
from floating_grammar import *
from PIL import Image, ImageTk
from PictureLevel import *
from Semantic_Learner import evaluate_semparse
from collections import defaultdict
from cossimforstem import sim_stemm
from back_and_forth import BackAndForth_Iterator

# inizializing grammar and learning algorithm
crude_lexicon={}
crude_rule = create_lex_rules()
threshold = -0.5
total_scores = defaultdict(lambda:defaultdict(int))

# initializing the windows
start = sg.Window("Hello!", layout_starting_screen)
actualgame = sg.Window("SHAPELURN", layout_game_screen, return_keyboard_events=True)
window = start

# define starting point
level = 1
i_picture = 1
n = 1
eval_attempts = 0

# level descriptions
level1 = "only describe one block, e.g.: 'There is a red circle'"
level2 = "describe one or more blocks, e.g: 'There are two blue forms'"
level3 = "describe relations between blocks, e.g.: 'There is a red circle under a blue square'"


def picture_path(level, i_picture, session_name, guess=False):
    """
    returns the path of the current picture given some details about it
    :param level: the level of the picture (int)
    :param i_picture: the picture number (int)
    :param session_name: the session name that has been chosen by the user (str)
    :param guess: whether the guess is included or not, default False (bool)
    :return: the path to the picture
    """
    if not guess:
        file_name = session_name + "_L" + str(level) + "_" + str(i_picture) + ".png"
    else:
        file_name = session_name + "_L" + str(level) + "_" + str(i_picture) + "_guess.png"
    path_pict = "./" + session_name + "/" + file_name
    return path_pict

def hiding_unhiding(event):
    if event == "-NEXT-":
        window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")
        window["-DESCRIPTION-"].update(level1)
        window["-INPUT-"].update(disabled=False)
        window["-INPINSTR-"].hide_row()
        window["-FEEDBACKINSTR-"].hide_row()
        window["-YES-"].update(disabled=False)
        window["-NO-"].update(disabled=False)
        window["-NO2-"].update(disabled=False)
        window["-SKIP-"].update(disabled=False)
        window["-YES-"].hide_row()
        window["-NEXTINSTR-"].hide_row()
        window["-NEXT-"].hide_row()
    elif event == "-ENTER-":
        # disabling further keyboard input and unhiding feedback buttons
        window["-INPUT-"].update(disabled=True)
        window["-ENTER-"].update(visible=False)
        window["-YES-"].unhide_row()
    elif event == "-YES-":
        window["-YES-"].hide_row()
        window["-ENTER-"].unhide_row()
        window["-INPUT-"].update(disabled=False)
        window["-ENTER-"].update(visible=True)
        window["-INPUT-"].update("")
    elif event == "-NO-" or "-NO2-" or "-SKIP-":
        window["-YES-"].hide_row()
        window["-ENTER-"].unhide_row()
        window["-INPUT-"].update(disabled=False)
        window["-ENTER-"].update(visible=True)
        window["-INPUT-"].update("")

# the game loop
while True:
    # event records which buttons were pressed, values store any keyboard input
    event, values = window.read()
    print(event, values)

    # to end the game
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # asks user for a session name under which their data will be stored
    if event == "-SESSION-":
        session_name = values["-SESSION-"]
        window["-START-"].update(disabled=False)

    # initializes a folder named after the session and an evaluation file inside that folder
    if event == "-START-":
        os.mkdir(session_name)
        evaluation_file = "./" + session_name + "/evaluation.csv"
        with open(evaluation_file, "w", encoding="utf-8") as f:
            first_line = "n\tlevel\tpicture\tinput\tmarked_picture\tattempts\ttree\n"
            f.writelines(first_line)
        # closing the the start window to start the actual game window
        window.close()
        window = actualgame

    # After reading the instructions this button starts the game and shows the first picture
    if event == "-NEXT-":
        # empty the guesses so they don't stack up with those from previous rounds
        guessed_blocks.clear()
        hiding_unhiding(event)

        # initializing the first picture
        current_pic = setPicParameters(level, i_picture, session_name)
        current_pic.draw()
        create_all_blocks(current_pic)
        # displaying the picture on the screen
        window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
        # storing the path to write into the evaluation file
        eval_picture = str(picture_path(level, i_picture, session_name))

    # takes a picture description as input from the user
    if event == "-INPUT-":
        window["-ENTER-"].update(disabled=False)
        inpt = values["-INPUT-"]

    # takes the complete input and processes it with grammar and learning algorithm to find the shapes the user referred to
    if event == "-ENTER-":
        hiding_unhiding(event)
        # stemming in order to find e.g. plural and singular forms and map them to the same lexical entry
        inpt = sim_stemm(inpt.lower(),list(crude_lexicon))

        # for storing in evaluation file
        eval_input = inpt

        # for any new word, map it to all possible rules and set initial weight for each rule to 0
        for word in inpt.split():
            if not word in crude_lexicon:
                crude_lexicon[word]=crude_rule[:]
                for rule in crude_rule:
                    total_scores[word][rule]=0
        gram = Grammar(crude_lexicon,rules,functions)
        print("checkpoint")
        # generate all possible trees given the current rules
        #lfs = BackAndForth_Iterator(gram.gen(inpt))
        #print(lfs)
        # with grouping included so every marking will only appear once, doesnt work though
        parse = gram.gen(inpt)
        print("parsing done")
        groups, sortedguesses = grouping(parse)
        print(sortedguesses)
        blocks = BackAndForth_Iterator(sortedguesses)
        print(blocks)
        try:
            current_marking = blocks.next()
            guess = []
            for b in groups[current_marking][0].guessed_blocks:
                guess.append((b.y, b.x))
            print(guess)
            current_pic.mark(guess)
            window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name, guess=True))
            # for evaluation file
            eval_marked_picture = str(picture_path(level, i_picture, session_name, guess=True))

        except StopIteration:
            pass

    # parser has found the correct tree, learning algorithm updates the weights for lexical items
    # next picture is displayed
    if event == "-YES-":
        hiding_unhiding(event)

        # updates weights
        lf = groups[current_marking][0]
        weights = evaluate_semparse(inpt,lf,gram,lfs.list) # what is lfs.list? How can we substitute it with the current structure? (the values of groups are parseItems = lfs)
        print("TEST",[weights[key] for key in weights],[0.0 for word in inpt],len(inpt.split()))
        if [weights[key] for key in weights] == [0.0 for word in inpt.split()]:
            print("Works!")
            for w in weights:
                if len(w)==2:
                    rule,word = w
                    crude_lexicon[word]=[rule]
        else:
            for w in weights:
                if len(w)==2:
                    rule,word = w
                    score = weights[w]
                    total_scores[word][rule]+=score
                    if total_scores[word][rule]<=threshold :
                        del total_scores[word][rule]
                        print("DELETE:",word,rule)
                        crude_lexicon[word].remove(rule)       
       
        gram = Grammar(crude_lexicon,rules,functions)
        for word in crude_lexicon:
            print(word,len(crude_lexicon[word]))

        # writes information about the round into the evaluation file
        eval_response = "yes"
        eval_attempts += 1
        with open(evaluation_file, "a", encoding="utf-8") as f:
            line = str(n) + "\t" + str(level) + "\t" + eval_picture + "\t" + eval_input + "\t" + eval_marked_picture + "\t" + str(eval_attempts) + "\t" + str(lf) + "\n"
            f.writelines(line)

        # update the level display
        n += 1
        if i_picture >= 10:
            i_picture = 0
            level += 1
            if level == 2:
                window["-DESCRIPTION-"].update(level2)
            elif level == 3:
                window["-DESCRIPTION-"].update(level3)
            else:
                print("thank you for participating!")
                break
        i_picture += 1

        # initialize new picture
        current_pic = setPicParameters(level, i_picture, session_name)
        current_pic.draw()
        create_all_blocks(current_pic)

        # display picture
        window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
        eval_picture = str(picture_path(level, i_picture, session_name))
        window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")
        eval_attempts = 0

    # parsing tree was not correct, produce new guess
    if event == "-NO-": # next
        # produce new guess (as above)
        try:
            current_marking = blocks.next()
            guess = []
            for b in groups[current_marking][0].guessed_blocks:
                guess.append((b.y, b.x))
            print(guess)
            current_pic.mark(guess)
            window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name, guess=True))
            eval_marked_picture = str(picture_path(level, i_picture, session_name, guess=True))
            eval_attempts += 1

        # if we run out of options, show the next picture
        except StopIteration:
            hiding_unhiding(event)

            if i_picture >= 10:
                i_picture = 0
                level += 1
            i_picture += 1
            current_pic = setPicParameters(level, i_picture, session_name)
            current_pic.draw()
            # Katharina added following line
            create_all_blocks(current_pic)
            window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
            window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")
            eval_picture = str(picture_path(level, i_picture, session_name))

    if event == "-NO2-": # previous
        # go to the step one before
        try:
            current_marking = blocks.previous()
            guess = []
            #print("GUESSEDBLOCKS", lf.guessed_blocks)
            for b in groups[current_marking][0].guessed_blocks:
                guess.append((b.y, b.x))
            current_pic.mark(guess)
            window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name, guess=True))
            eval_marked_picture = str(picture_path(level, i_picture, session_name, guess=True))
            eval_attempts -= 1

        # if we run out of options, show the next picture
        except StopIteration:
            print("HÄÄÄÄ")
            hiding_unhiding(event)

            if i_picture >= 10:
                i_picture = 0
                level += 1
            i_picture += 1
            current_pic = setPicParameters(level, i_picture, session_name)
            current_pic.draw()
            # Katharina added following line
            create_all_blocks(current_pic)
            window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
            eval_picture = str(picture_path(level, i_picture, session_name))
            window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")

    # skip if you accidentally entered a wrong input
    if event == "-SKIP-":
        hiding_unhiding(event)
        
        with open(evaluation_file, "a", encoding="utf-8") as f:
            line = str(level) + "\t" + eval_picture + "\t" + eval_input + "\t" + eval_marked_picture + "\t" + "SKIPPED" + "\t" + str(lf) + "\n"
            f.writelines(line)

        current_pic = setPicParameters(level, i_picture, session_name)
        current_pic.draw()
        # Katharina added following line
        create_all_blocks(current_pic)
        window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
        eval_picture = str(picture_path(level, i_picture, session_name))
        window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")
        eval_attempts = 0
       

window.close()
