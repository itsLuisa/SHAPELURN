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

"""
This script brings together the all parts of the project and creates the gui and runs the actual game.
"""

# inizializing grammar and learning algorithm
crude_lexicon={}
crude_rule = create_lex_rules()
threshold = -0.1
upper_threshold = 1.0
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
second_version = False

# level descriptions
level1 = "Use only the shapes and/or the number of blocks for your description, \n e.g.: 'a circle' or 'two forms'"
level2 = "You can additionally describe the blocks by color, \n e.g: 'two blue forms'"
level3 = "Now you can describe relations between blocks and use conjunction (please don't use colors),\ne.g.: 'a circle under a square'"
level4 = "Describe whatever you want!"

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
    """
    regulates which buttons and other items are visible and which aren't
    :param event: the event that has been cause by the user such as pressing a button or typing in something
    :return: nothing
    """
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
        window["-LEVELUP-"].hide_row()
        window["-CONTINUE-"].update(disabled=False)
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

    # initializes a folder named after the session and two evaluation files inside that folder
    if event == "-START-":
        os.mkdir(session_name)
        evaluation_file = "./" + session_name + "/evaluation.csv"
        weights_file = "./" + session_name + "/weights.csv"
        rule_probs = dict()
        learning = defaultdict(int)
        with open(evaluation_file, "w", encoding="utf-8") as f:
            first_line = "n\tlevel\tn_pic\tpicture_path\tguess_path\tinput\tattempts\tn_deleted_rules\tn_guessed_blocks\n"
            f.writelines(first_line)
        with open(weights_file, "w", encoding="utf-8") as g:
            first_line = "level\trule\tweight\tdeleted_rules\n"
            g.writelines(first_line)
        # closing the the start window to start the actual game window
        window.close()
        window = actualgame

    # After reading the instructions this button starts the game and shows the first picture
    if event == "-NEXT-":
        # empty the guesses so they don't stack up with those from previous rounds
        guessed_blocks.clear()
        hiding_unhiding(event)

        # initializing the first picture
        current_pic = setPicParameters(level, i_picture, session_name, second_version)
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

        # generate all possible parses given the current rules
        parse = gram.gen(inpt)
        print("parsing done")

        # with grouping included every marking will only appear once
        groups, sortedguesses = grouping(parse)
        print(sortedguesses)

        # creates an iterator for the user to move forward and backward through the guesses
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

    # parser has found the correct parse, learning algorithm updates the weights for lexical items
    # next picture is displayed
    if event == "-YES-":
        hiding_unhiding(event)
        n_deleted_rules = 0
        deleted_rules = list()
        # updates weights
        lf = groups[current_marking]
        weights = evaluate_semparse(inpt,lf,gram,parse)
        if all([weights[key]==0 for key in weights]):
            print("Works!") # if there is only the correct mapping left
            word_rule = defaultdict(set)
            for w in weights:
                if len(w)==2:
                    word,rule=w
                    word_rule[word].add(rule)
            for word in word_rule:
                if word in crude_lexicon:
                    for categorie,rule,prob in crude_lexicon[word][:]:
                        if not rule in word_rule[word]:
                            crude_lexicon[word].remove((categorie,rule,prob))
                    
                    
        else:
            for w in weights:
                if len(w)==2:
                    word,rule = w
                    if word == "":
                        continue
                    score = weights[w]
                    total_scores[word][rule]+=score
                    if total_scores[word][rule]<=threshold:
                        del total_scores[word][rule]
                        print("DELETE:",word,rule)
                        n_deleted_rules += 1
                        deleted_rules.append((word, rule))
                        for r in crude_lexicon[word][:]:
                            if r[1] == rule:
                                crude_lexicon[word].remove(r)

            # delete rules with weight equal or below 0 if one rule for a word reaches weight of 1
            rules_to_delete = set()
            for word in total_scores:
                above_one = False
                # check whether one rule reaches the threshold
                for rule in total_scores[word]:
                    if total_scores[word][rule] >= upper_threshold:
                        above_one = True
                        break
                # check which rules are equal or below 0 and should be deleted
                if above_one:
                    for rule in total_scores[word]:
                        if total_scores[word][rule] <= 0:
                            rules_to_delete.add((word, rule))
            # delete the determined rules
            for (word, rule) in rules_to_delete:
                del total_scores[word][rule]
                print("DELETE:", word, rule)
                n_deleted_rules += 1
                deleted_rules.append((word, rule))
                for r in crude_lexicon[word][:]:
                    if r[1] == rule:
                        crude_lexicon[word].remove(r)

            # update crude lexicon
            for word in crude_lexicon:
                for ruleindex in range(0,len(crude_lexicon[word])):
                    crude_lexicon[word][ruleindex] = (crude_lexicon[word][ruleindex][0],crude_lexicon[word][ruleindex][1],total_scores[word][crude_lexicon[word][ruleindex][1]])
                    
        
        gram = Grammar(crude_lexicon,rules,functions)
        print("\nNew Lexicon:")
        for word in crude_lexicon:
            print("---",word,"---")
            for rule in crude_lexicon[word]:
                print(rule)

        # store weights for evaluation
        for rule, val in list(weights.items()):
            learning[rule] += val
        rule_probs[n] = learning
        lf1 = lf[0]

        # writes information about the round into the evaluation file
        n_guessed_blocks = len(guess)
        eval_response = "yes"
        eval_attempts += 1
        with open(evaluation_file, "a", encoding="utf-8") as f:
            line = str(n) + "\t" + str(level) + "\t" + str(i_picture) + "\t" + eval_picture + "\t" + eval_marked_picture + "\t" + eval_input + "\t" + str(eval_attempts) + "\t" + str(n_deleted_rules) + "\t" + str(n_guessed_blocks) + "\n"
            f.writelines(line)

        # update the level display
        n += 1
        # used to enable that level 2 consists of 5 pictures more than the others with potentially more than three blocks
        second_version = False
        if i_picture >= 15 and i_picture < 20 and level == 2:
            second_version = True
        elif i_picture >= 15:
            second_version = False
            # after each level, update the weights file
            with open(weights_file, "a", encoding="utf-8") as g:
                for id, rule in enumerate(learning.items()):
                    try:
                        line = str(level) + "\t" + str(rule[0]) + "\t" + str(rule[1]) + "\t" + str(
                            deleted_rules[id]) + "\n"
                    except IndexError:
                        line = str(level) + "\t" + str(rule) + "\t" + str(rule[1]) + "\t-\n"
                    g.writelines(line)

            i_picture = 0
            level += 1
            if level == 2:
                window["-DESCRIPTION-"].update(level2)

            elif level == 3:
                window["-DESCRIPTION-"].update(level3)

            elif level == 4:
                window["-DESCRIPTION-"].update(level4)

        i_picture += 1

        # initialize new picture
        current_pic = setPicParameters(level, i_picture, session_name, second_version)
        current_pic.draw()
        create_all_blocks(current_pic)

        # display picture
        window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
        eval_picture = str(picture_path(level, i_picture, session_name))
        window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")
        eval_attempts = 0

        # transfer level up screen
        if level >= 2 and level < 4 and i_picture == 1:
            window["-INPUT-"].hide_row()
            window["-LEVELUP-"].unhide_row()
            window["-LEVELUP-"].update("You reached the next level!")
        elif level == 5 and i_picture == 1:
            window["-INPUT-"].hide_row()
            window["-LEVELUP-"].unhide_row()
            window["-LEVELUP-"].update("Thank you for participating!")
            window["-CONTINUE-"].update(visible=False)
            window["-NEXTINSTR-"].unhide_row()
            window["-NEXTINSTR-"].update("You can now close the window:)")

    # level up screen, game continues when this button is pressed
    if event == "-CONTINUE-":
        window["-LEVELUP-"].hide_row()
        window["-INPUT-"].unhide_row()

    # parse was not correct, produce new guess
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
            current_pic = setPicParameters(level, i_picture, session_name, second_version)
            current_pic.draw()
            create_all_blocks(current_pic)
            window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
            window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")
            eval_picture = str(picture_path(level, i_picture, session_name))

    # see the previous guess in case one skipped the right guess accidentally
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
            current_pic = setPicParameters(level, i_picture, session_name, second_version)
            current_pic.draw()
            create_all_blocks(current_pic)
            window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
            eval_picture = str(picture_path(level, i_picture, session_name))
            window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")

    # skip if you accidentally entered a wrong input
    if event == "-SKIP-":
        hiding_unhiding(event)

        # update the evaluation file
        with open(evaluation_file, "a", encoding="utf-8") as f:
            line = str(n) +"\t"+ str(level)  +"\t"+str(i_picture) + "\t" + eval_picture + "\t" + "NA" + "\t" + eval_input + "\t" + "NA" + "\t" + "NA" + "\t" + "NA" + "\n"
            f.writelines(line)

        current_pic = setPicParameters(level, i_picture, session_name, second_version)
        current_pic.draw()
        create_all_blocks(current_pic)
        window["-IMAGE-"].update(filename=picture_path(level, i_picture, session_name))
        eval_picture = str(picture_path(level, i_picture, session_name))
        window["-LEVEL-"].update("Level " + str(level) + ", Picture " + str(i_picture) + ":")
        eval_attempts = 0
       

window.close()
