from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import PySimpleGUI as sg
import re
from PIL import Image

def captcha_builder(resp):
    with open('captcha.svg', 'w') as f:
        f.write(re.sub('(<path d=)(.*?)(fill="none"/>)', '', resp['captcha']))

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    im = Image.open('captcha.png')
    im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
    im.save('captcha.gif')

    layout = [[sg.Image('captcha.gif')],
          [sg.Text("Enter Captcha Below")],
          [sg.Input()],
          [sg.Button('Submit', bind_return_key=True)]]

    window = sg.Window('Enter Captcha', layout)
    event, values = window.read()
    window.close()
    return values[1]
