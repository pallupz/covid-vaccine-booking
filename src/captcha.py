from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import PySimpleGUI as sg
import re


def captcha_builder(resp):
    with open('captcha.svg', 'w') as f:
        f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', resp['captcha']))

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    layout = [[sg.Image('captcha.png')],
              [sg.Text("Enter Captcha Below")],
              [sg.Input(key='inp')],
              [sg.Button('Submit', bind_return_key=True)]]

    window = sg.Window('Enter Captcha', layout, finalize=True)
    window.TKroot.focus_force()         # focus on window
    window.Element('inp').SetFocus()    # focus on field
    window.BringToFront() #To bring the captcha window infront of all active windows
    event, values = window.read()
    window.close()
    return values['inp']

