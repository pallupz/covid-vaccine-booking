def captcha_buider(resp):
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPM
    from PIL import Image
    import cv2

    with open('captcha.svg', 'w') as f:
        f.write(resp['captcha'])

    drawing = svg2rlg('captcha.svg')
    renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

    img = cv2.imread("captcha.png")
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow(grey)
    
    if cv2.waitkey(1) == ord("q"):
        cv2.destroyAllWindows()
