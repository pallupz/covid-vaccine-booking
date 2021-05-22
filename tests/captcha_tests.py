
def test_captcha_builder():
    from PIL import Image
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    import PySimpleGUI as sg

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    im = Image.open('captcha.png')
    im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
    im.save('captcha.gif')

    layout = [[sg.Image('captcha.gif')],
          [sg.Text("Enter Captcha Below")],
          [sg.Input(key='input')],
          [sg.Button('Submit', bind_return_key=True)]]

    print("window opening ...")
    window = sg.Window('Enter Captcha', layout, finalize=True)
    window.TKroot.focus_force()         # focus on window
    window.Element('input').SetFocus()  # focus on field
    event, values = window.read()
    window.close()

    captcha_value = values['input']
    expected_captcha_value = "SNNvu"
    if captcha_value == expected_captcha_value:
        print("Yeah !!! you have entered captcha. This means you are all set to render required captcha at the time of booking ...\n")
    else:
        print("\nOhh NO !!! you have entered wrong captcha : %s while expected: %s" % (captcha_value, expected_captcha_value))
        print("Check if you are missing any required python packages\n\n")

def test_captcha_builder_auto():
    import re, json, base64, os, sys, time
    from bs4 import BeautifulSoup

    model = open(os.path.join(os.path.dirname(sys.argv[0]), "../src/model.txt")).read()
    svg_data = open("captcha.svg", "r")
    soup = BeautifulSoup(svg_data, 'html.parser')
    model = json.loads(base64.b64decode(model.encode('ascii')))
    CAPTCHA = {}

    print("Started solving captcha...")
    tic = time.perf_counter()

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
    
    toc = time.perf_counter()
    if CAPTCHA_STRING == "SNNvu":
        print(f"Captcha solve success: {CAPTCHA_STRING}")
        print(f"It took {toc - tic:0.5f} seconds to solve captcha")
    else:
        print(f"Task finished with wrongly predicted value - {CAPTCHA_STRING}")

def test_python_packages():
    try:
        from PIL import Image
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM
        import PySimpleGUI as sg
        import re, json, base64, os, sys
        from bs4 import BeautifulSoup
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
test_captcha_builder_auto()
