from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import PySimpleGUI as sg
import re
from PIL import Image
from anticaptchaofficial.imagecaptcha import imagecaptcha

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


def captcha_builder_auto(resp, api_key):
    with open('captcha.svg', 'w') as f:
        f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', resp['captcha']))

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    
    solver = imagecaptcha()
    solver.set_verbose(1)
    solver.set_key(api_key)
    captcha_text = solver.solve_and_return_solution("captcha.png")

    if captcha_text != 0:
        print(f"Captcha text: {captcha_text}")
    else:
        print(f"Task finished with error: {solver.error_code}")

    return captcha_text
