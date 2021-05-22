from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import PySimpleGUI as sg
import re
from PIL import Image
from bs4 import BeautifulSoup
import json
import base64
import os
import sys

def captcha_builder_manual(resp):
    with open('captcha.svg', 'w') as f:
        f.write(re.sub('(<path d=)(.*?)(fill="none"/>)', '', resp['captcha']))

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    im = Image.open('captcha.png')
    im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
    im.save('captcha.gif')

    layout = [[sg.Image('captcha.gif')],
          [sg.Text("Enter Captcha Below")],
          [sg.Input(key='input')],
          [sg.Button('Submit', bind_return_key=True)]]

    window = sg.Window('Enter Captcha', layout, finalize=True)
    window.TKroot.focus_force()         # focus on window
    window.Element('input').SetFocus()    # focus on field
    event, values = window.read()
    window.close()
    return values['input']


def captcha_builder_auto(resp):
    model = open(os.path.join(os.path.dirname(sys.argv[0]), "model.txt")).read()
    svg_data = resp['captcha']
    soup = BeautifulSoup(svg_data, 'html.parser')
    model = json.loads(base64.b64decode(model.encode('ascii')))
    CAPTCHA = {}

    for path in soup.find_all('path', {'fill': re.compile("#")}):
        ENCODED_STRING = path.get('d').upper()
        INDEX = re.findall('M(\d+)', ENCODED_STRING)[0]
        ENCODED_STRING = re.findall("([A-Z])", ENCODED_STRING)
        ENCODED_STRING = "".join(ENCODED_STRING)
        CAPTCHA[int(INDEX)] = model.get(ENCODED_STRING)

    CAPTCHA = sorted(CAPTCHA.items())
    CAPTCHA_STRING = ''

    for char in CAPTCHA:
        CAPTCHA_STRING += char[1]
    return CAPTCHA_STRING