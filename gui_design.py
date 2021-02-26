import PySimpleGUI as sg

starting_screen = [
    [
        sg.Text("Hello! Welcome to SHAPELURN, where you can teach the computer any language of your choice!\nYou will be looking at different pictures and describing them to the computer in one sentence.\nPlease use rather short sentences and try not to use negation and conjunction only on full sentences.")
    ],
    [
       sg.Text("In order to evaluate our model we would like to collect your data.\nPlease enter any name under which you would like to save your data.")
    ],
    [
        sg.Text("Enter session name:"),
        sg.In(size=(25, 1), enable_events=True, key="-SESSION-"),
        sg.Button("Start Game", key="-START-", disabled=True)
    ]
]

# game screen contents
game_screen = [
    [
        sg.Text("Level xx, Picture xx: <- This is the level display, you will play 3 levels each containing 10 pictures.", key="-LEVEL-")
    ],
    [
        sg.Text("\n[Here you will see a 4x4 grid picture displaying objects of different shape and color.]\n", key="-DESCRIPTION-")
    ],
    [
        sg.Image(key="-IMAGE-")  # can display any png image
    ],
    [
        sg.Text("Describe the picture:", key="-INSTRUCTION-"),
        sg.In(size=(25, 1), enable_events=True, key="-INPUT-", disabled=True), # takes keyboard input from user
        sg.Button("Enter", key="-ENTER-", disabled=True)
    ],
    [
        sg.Text("This is where you enter your sentence. Press the enter button once you are done.\n", key="-INPINSTR-")
    ],
    [
        sg.Text("Did you refer to this?"),
        sg.Button("YES", key="-YES-", disabled=True),
        sg.Button("next", key="-NO-", disabled=True),
        sg.Button("back",key="-NO2-",disabled=True),
        sg.Button("SKIP", key="-SKIP-", disabled=True)
    ],
    [
        sg.Text(
            "This will show up after you have entered your sentence.\nThe program will make a guess about what part of the picture your description was referring to by marking it with a black frame.\nPlease only click YES when ALL of the corresponding positions are marked.\nIf you accidentally entered a wrong description you can use SKIP to go on with the next picture.\n",
            key="-FEEDBACKINSTR-"
        )
    ],
    [
        sg.Text("Whenever you're ready:", key="-NEXTINSTR-")
    ],
    [
        sg.Button("Press here to show first picture", key="-NEXT-")
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