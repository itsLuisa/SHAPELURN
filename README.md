# Semantic-Parsing-of-picture-descriptions
This project is part of the Softwareproject "Language, Action and Perception".

General research question:  Can we implement a model that learns a natural language from scratch through interaction?

Focused research question:  Can we teach a computer a mapping from natural language picture descriptions to a logical representation?

<div style="float:right;"><img src="https://user-images.githubusercontent.com/36165516/107762120-cf5e8980-6d2c-11eb-97d8-30ea3c3ea5a5.jpg" alt="Logo" height="180" align="right"></img></div>

# SHAPELURN
# An Interactive Language Learning Game

## Demo of the SHAPELURN
To play the our language learning game you only have to clone the repository and run the gui_simple.py script. 
You will be asked to enter a name for your session and the programm will then create a new folder with your chosen name in the source code directory. 
In this folder the result data from your game  will be stored. (If your are testing the game for us in order to collect data for our evaluation of the system, this folder contains all the data we need from you. However, additional feedback with respect to the overall game experience, clearity of instructions,... is very welcome)

**Requirements**<br>
Python 3 <br>
PIL (Pillow) <br>
PySimpleGUI <br>
Numpy <br>

To install the required packages run 
```pip install -r requirements.txt```

## Basic Instructions 

Hello! Welcome to SHAPELURN, where you can teach the computer any language of your choice!<br>
You will be looking at different pictures and describing them to the computer in one sentence.<br>
There will be four levels with different constraints on the descriptions.<br>
Please use short sentences in the first two levels and do not use negation at all.<br>

Hello! Welcome to SHAPELURN, where you can teach the computer any language of your choice!<br>
You will be looking at different pictures and describing them to the computer in one sentence. <br>
Please use rather short sentences and try not to use negation and conjunction."

In order to evaluate our model we would like to collect your data.<br>
Please enter any name under which you would like to save your data on your local machine.

Constraints on descriptions depending on level: <br>
* Level 1: Use only the shapes and/or the number of blocks for your description, e.g.: *There is a circle* or *There are two forms*
* Level 2: You can additionally describe the blocks by color, e.g: *There are two blue forms*
* Level 3: Now you can describe relations between blocks and use conjunction, e.g.: *There is a red circle under a blue square*
* Level4: Describe whatever you want!

For the detailed instructions and examples please refer to the [Wiki](https://github.com/itsLuisa/Semantic-Parsing-of-picture-descriptions/wiki)

## References

The project idea is based on Wang, S. I., Liang, P., & Manning, C. D. (2016). Learning language games through interaction. arXiv preprint arXiv:1606.02447. <br>
Our parsing and learning framework is based on Liang, Percy and Christopher Potts. 2014. Bringing machine learning and compositional semantics together. *Annual Review of Linguistics* 1(1): 355–376. and uses code from [the corresponding demonstration code](https://github.com/cgpotts/annualreview-complearning).

## Files 
* folder marked_pictures: needed for running grammar.py, guesses for the test utterances in semdata.py will be saved here
* folder pictures: example pictures as created by PictureLevel.py

* BlockPictureGenerator.py: automatically creates and saves the pictures **documented**
* CalculCoordinates.py: used to calculate the coordinates for the picture generation in BlockPictureGenerator.py **documented**
* cosimforstem.py: cosine similarity based heuristic for stemming words from an unknown language **documented**
* PictureLevel.py: generates a picture for a specified level by calling BlockPictureGenerator.py with corresponding parameters **documented**
* Semantic_Learner.py:  
* eval_helper.py: functions needed in grammar.py to evaluate truth of description **documented**
* floating_grammar.py: defines the grammer, the evalation of logical forms and the floating parser **documented**
* grammar.py: defines the grammar, the evaluation of logical forms and the basic cky parser **documented**
* gui_simple.py: working GUI **documented**
* gui_simple_floating.py
* back_and_forth.py: An iterator class, that can go back and forth through a list
* learning.py: the Stochastic Gradient Descent learn algorithm 
* semdata.py: training and test sentences 
* word.py and world2.png: example picture used for demo of grammar.py with test sentences from semdata.py
