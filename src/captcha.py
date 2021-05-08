from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import PySimpleGUI as sg
import cv2


def captcha_builder(resp):
    with open('captcha.svg', 'w') as f:
        f.write(resp['captcha'])

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    img = cv2.imread("captcha.png", 0)
    cv2.imwrite("captcha.png", img)

    layout = [[sg.Image('captcha.png')],
              [sg.Text("Enter Captcha Below")],
              [sg.Input()],
              [sg.Button('Submit', bind_return_key=True)]]

    window = sg.Window('Enter Captcha', layout)
    event, values = window.read()
    window.close()
    return values[1]

