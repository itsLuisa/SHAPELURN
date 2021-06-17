import PySimpleGUI as sg

"""
Defines some of the layout of the gui and the initial instruction screens
"""

default_font = "Helvetica 12"

# description of the game and entering the session name
starting_screen = [
    [
        sg.Text("Hello! Welcome to SHAPELURN, where you can teach the computer any language of your choice!\nYou will be looking at different pictures and describing them to the computer in one sentence.\nThere will be four levels with different constraints on the descriptions.\nPlease use short sentences in the first two levels and do not use negation at all.", font=default_font)
    ],
    [
       sg.Text("In order to evaluate our model we would like to collect your data.\nPlease enter any name under which you would like to save your data on your local machine.", font=default_font)
    ],
    [
        sg.Text("Enter session name:", font=default_font),
        sg.In(size=(25, 1), enable_events=True, key="-SESSION-", font=default_font),
        sg.Button("Start Game", key="-START-", disabled=True, font=default_font)
    ]
]

# game screen contents
game_screen = [
    [
        sg.Text("Level xx, Picture xx: <- This is the level display, you will play 4 levels.", key="-LEVEL-", font=default_font)
    ],
    [
        sg.Text("\n[Here you will see a 4x4 grid picture displaying objects of different shape and color.]\n", key="-DESCRIPTION-", font=default_font)
    ],
    [
        sg.Image(key="-IMAGE-", size=(2,2))  # can display any png image
    ],
    [
        sg.Text("Describe the picture:", key="-INSTRUCTION-", font=default_font),
        sg.In(size=(25, 1), enable_events=True, key="-INPUT-", disabled=True, font=default_font), # takes keyboard input from user
        sg.Button("Enter", key="-ENTER-", disabled=True, font=default_font)
    ],
    [
        sg.Text("This is where you enter your sentence. Press the enter button once you are done.\n", key="-INPINSTR-", font=default_font)
    ],
    [
        sg.Text("Did you refer to this?", font=default_font),
        sg.Button("YES", key="-YES-", disabled=True, font=default_font), # give feedback using these buttons
        sg.Button("BACK", key="-NO2-", disabled=True, font=default_font),
        sg.Button("NEXT", key="-NO-", disabled=True, font=default_font),
        sg.Button("SKIP", key="-SKIP-", disabled=True, font=default_font)
    ],
    [
        sg.Text(
            "This will show up after you have entered your sentence.\nThe program will make a guess about what part of the picture your description was referring to by marking it with a black frame.\nPlease only click YES when ALL of the corresponding positions are marked.\nIf the guess does not match your description choose NEXT. With BACK you can go back to the previous guesses if you accidentally clicked NEXT.\nIf you accidentally entered a wrong description you can use SKIP to go on with the next picture.\nImportant: Do not try to move the window of the GUI while it is processing your description or your feedback as this will lead to a bug in the presentation of the GUI!",
            key="-FEEDBACKINSTR-", font=default_font
        )
    ],
    [
        sg.Text("This button will appear when you level up:", key="-LEVELUP-", font=default_font),
        sg.Button("CONTINUE", key="-CONTINUE-", disabled=True, font=default_font)
    ],
    [
        sg.Text("Whenever you're ready:\t", key="-NEXTINSTR-", font=default_font)
    ],
    [
        sg.Button("Press here to show first picture", key="-NEXT-", font=default_font)
    ]
]

# the layouts for both screens
layout_starting_screen = [
    [
        sg.Column(starting_screen)
    ]
]

layout_game_screen = [
    [
        sg.Column(game_screen)
    ]
]
