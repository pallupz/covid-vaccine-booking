def captcha_buider(resp):
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    from PIL import Image

    with open('captcha.svg', 'w') as f:
        f.write(resp['captcha'])

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    img = Image.open('captcha.png')
    img.show()