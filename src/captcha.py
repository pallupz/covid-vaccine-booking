def captcha_buider(resp):
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    import PySimpleGUI as sg

    with open('captcha.svg', 'w') as f:
        f.write(resp['captcha'])

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    layout = [  [ sg.Image('captcha.png') ],
	    		[sg.Text("Enter Captcha Below")],
                [sg.Input()],
                [sg.Button('Submit',bind_return_key=True)] ]

    window  = sg.Window('Enter Captcha',layout)
    
    event, values = window.read()
    
    window.close()
    
    return values[1]