
def test_captcha_builder():
    from PIL import Image
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    import PySimpleGUI as sg
    import re
    #with open('captcha.svg', 'w') as f:
    #    f.write(re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', resp['captcha']))
    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    im = Image.open('captcha.png')
    im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
    im.save('captcha.gif')

    layout = [[sg.Image('captcha.gif')],
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
        print("Yeah !!! you have entered captcha. This means you are all set to render required captcha at the time of booking ...\n")
    else:
        print("\nOhh NO !!! you have entered wrong captcha : %s while expected: %s" % (captcha_value, expected_captcha_value))
        print("Check if you are missing any required python packages\n\n")

def test_captcha_builder_auto(api_key):
    from PIL import Image
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    from anticaptchaofficial.imagecaptcha import imagecaptcha
    import re, time
    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    solver = imagecaptcha()
    solver.set_verbose(1)
    solver.set_key(api_key)

    print("Started solving captcha...")
    tic = time.perf_counter()
    captcha_text = solver.solve_and_return_solution("captcha.png")
    toc = time.perf_counter()

    if captcha_text == "SNNvu":
        print(f"Captcha solve success: {captcha_text}")
        print(f"It took {toc - tic:0.4f} seconds to solve captcha")
    else:
        print(f"Task finished with error: {solver.error_code} - {captcha_text}")

    return captcha_text

def test_python_packages():
    try:
        from PIL import Image
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        import PySimpleGUI as sg
        import re
    except Exception:
        print("\n!!!!! Looks like you are missing required python packages. Please look at requirements.txt !!!!")
        exit(1)

def test_tkinter_lib():
    try:
        from PIL import Image
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        import PySimpleGUI as sg
        import re
    except Exception:
        print("\n!!!!! Looks like you are missing required python packages. Please look at requirements.txt !!!!")
        exit(1)
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


test_python_packages()
test_tkinter_lib()
test_captcha_builder()
test_captcha_builder_auto("APIKEY") #http://anti-captcha.com