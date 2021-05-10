from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import PySimpleGUI as sg
import re

def test_captcha_builder():
    #with open('captcha.svg', 'w') as f:
    #    f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', resp['captcha']))

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")
    print("window opening ...")
    layout = [[sg.Image('captcha.png')],
              [sg.Text("Enter Captcha Below")],
              [sg.Input()],
              [sg.Button('Submit', bind_return_key=True)]]

    print("window opening ...")
    window = sg.Window('Enter Captcha', layout)
    event, values = window.read()
    window.close()
    captcha_value = values[1]
    expected_captcha_value = "SNNvu"
    if captcha_value == expected_captcha_value:
        print("Yeah !!! you have entered captcha. This means you are all set to render required captcha at the time of booking ...")
    else:
        print("Ohh NO !!! you have entered wrong captcha : %s while expected: %s" % (captcha_value, expected_captcha_value))
        print("Check if you are missing any required packages")

def test_tkinter_lib():
    try:
        import tkinter
        tkinter_version = tkinter.Tcl().eval('info patchlevel')
        print("Installed tkinter_version: %s \n %s" % (tkinter_version, "-"*100))
        print('Opening test window. Click on "Quit" to run further tests')
        tkinter._test()
    except Exception:
        print("\n!!!!! Looks like you are missing required 'tkinter' python package !!!!")
        print("Try installing looking at following resources:")
        print("1. https://tkdocs.com/tutorial/install.html#install-win-python")
        print("2. https://stackoverflow.com/questions/25905540/importerror-no-module-named-tkinter")
        print()
        exit(1)



test_tkinter_lib()
test_captcha_builder()
