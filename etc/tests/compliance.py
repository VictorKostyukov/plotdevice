size(900,2700)

def header():
    font("Helvetica Neue", 18)
    text("PlotDevice Compliance Tests", 20, 60)
    stroke(0.5)
    line(0,60,WIDTH,60)
    fontsize(12)
    nostroke()
    text("This functional suite tests all the available PlotDevice functions." , 20, 80, width=275)
    fontsize(10)
    
def primitives(x, y):
    nostroke()
    rect(x, y, 50, 50)
    x += 75
    rect(x, y, 50, 50, .25)
    x += 75
    oval(x, y, 50, 50)
    x += 75
    poly(x+25, y+25, 25, sides=6)
    x += 75
    oval(x, y, 50, 50, range=180) # chocolate
    arc(x+25, y+25, 25, range=(180,0), fill=.5) # peanutbutter
    x += 75
    star(x+25, y+25, 20, outer=25, inner=15)
    x += 75
    arrow(x+50, y+25, 50)
    x += 75
    arrow(x+60, y+25, 50, type=FORTYFIVE).rotate(-45)
    
def basictext(x, y):
    text("Hello", x, y)

    for alignment in (LEFT, CENTER, RIGHT):
        x += 60
        align(alignment)
        stroke(0.5)
        nofill()
        rect(x, y-12,50,15, dash=3)
        fill(0)
        text("Hello", x, y, width=50)
    align(LEFT)

def alignedtext(x, y):
    for alignment in (LEFT, CENTER, RIGHT):
        align(alignment)
        stroke(.5)
        line(x,y-12, x,y+12, dash=3)
        fill(0)
        text("Hello", x, y)
        x += 115
    align(LEFT)

def textblock(x, y):
    for alignment in (LEFT, CENTER, RIGHT, JUSTIFY):
        align(alignment)
        stroke(.5)
        nofill()
        rect(x, y-12, 50, 50, dash=3)
        fill(0)
        text("Lorem ipsum dolor sit amet, consectetuer adipiscing elit.", x, y, width=50, height=50)
        x += 80

    align(LEFT)
    
def greyscale(x, y):
    stroke(.9)
    colormode(RGB)
    align(CENTER)
    for i in range(11):
        fill(i/10.0)
        rect(x, y, 50, 50)
        fill(0)
        text(str(i), x, y+62, 50)
        x += 60
    align(LEFT)

def alphas(x, y):
    stroke(.9)
    colormode(RGB)
    align(CENTER)
    for i in range(11):
        fill(0, i/10.0)
        rect(x, y, 50, 50)
        fill(0)
        text(str(i), x, y+62, 50)
        x += 60
    align(LEFT)
    
def _clr(x, y, *args):
    fill(args)
    rect(x, y, 50, 50)
    fill(0)
    align(CENTER)
    text(str(args), x-5, y+62, 60)
    align(LEFT)
    stroke(.5)
    return x + 60

def rgbColors(x, y):
    stroke(.9)
    colormode(RGB)
    x = _clr(x, y, 0,0,0)
    x = _clr(x, y, 0,0,1)
    x = _clr(x, y, 0,1,0)
    x = _clr(x, y, 0,1,1)
    x = _clr(x, y, 1,0,0)
    x = _clr(x, y, 1,0,1)
    x = _clr(x, y, 1,1,0)
    x = _clr(x, y, 1,1,1)
    
def cmykColors(x, y):
    stroke(.9)
    colormode(CMYK)
    x = _clr(x, y, 0,0,0,1)
    x = _clr(x, y, 0,0,1,0)
    x = _clr(x, y, 0,1,0,0)
    x = _clr(x, y, 1,0,0,0)
    x = _clr(x, y, 1,1,0,0)
    x = _clr(x, y, 0,1,1,0)
    x = _clr(x, y, 1,0,1,0)
    x = _clr(x, y, 1,1,1,0)
    x = _clr(x, y, 0,0,0,0)

def hsbColors(x, y):
    stroke(.9)
    colormode(HSB)
    x = _clr(x, y, 0,0,0) # black

    x = _clr(x, y, 0,1,1)  # bright
    x = _clr(x, y, .3,1,1)
    x = _clr(x, y, .5,1,1)

    x = _clr(x, y, 0,1,.5) # darker
    x = _clr(x, y, .3,1,.5)
    x = _clr(x, y, .5,1,.5)

    x = _clr(x, y, 0,.2,1) # pastel
    x = _clr(x, y, .3,.2,1)
    x = _clr(x, y, .5,.2,1)
    
    x = _clr(x, y, 0,0,1) # white

def images(x, y):
    zoom = 0.5
    w, h = measure(file("icon.png"))
    y -= h/2.0*zoom
    bmp = image("icon.png", x,y, width=w/2, plot=False) # half size
    plot(bmp)
    with translate(125,0), rotate(90):                  # half size, rotated
        plot(bmp) 
    with translate(259,0), rotate(180), scale(2.0):     # doubled (back to full size), flipped
        plot(bmp) 
    with translate(375,0), scale(2.0), shadow(.8, blur=10): # doubled (back to full size), dropshadowed
        plot(bmp) 
    
def marker(y,h=25):
    colormode(CMYK)
    stroke(1, 0.1, 0.1, 0.1)
    line(0, y+h, WIDTH, y+h)

# Draw the header
header()

# Draw the primitives at their first position
marker(140)
nostroke()
text("Basic primitives", 20, 165)
primitives(140,140)

# Simple translation
translate(0, 140)
marker(140)
nostroke()
text("Translated primitives", 20, 165)
primitives(140,140)

# Translation and rotation
translate(0, 140)
marker(140)
nostroke()
text("Rotated primitives", 20, 165)
push()
rotate(45)
primitives(140,140)
pop()

# Scaling
translate(0, 140)
marker(140)
nostroke()
text("Scaled primitives", 20, 165)
push()
scale(0.5)
primitives(140,140)
pop()

# Scaling
translate(0, 140)
marker(140)
nostroke()
text("Shadowed primitives", 20, 165)
push()
scale(0.5)
with shadow('#aaa', 5, 7):
    primitives(140,140)
pop()

# Greyscale
translate(0, 140)
marker(140)
nostroke()
text("Greyscale", 20, 165)
greyscale(140, 140)

# Alphas
translate(0, 140)
marker(140)
nostroke()
text("Alphas", 20, 165)
alphas(140, 140)


# RGB Colors
translate(0, 140)
marker(140)
nostroke()
text("RGB Colors", 20, 165)
rgbColors(140, 140)

# HSB Colors
translate(0, 140)
marker(140)
nostroke()
text("HSB Colors", 20, 165)
hsbColors(140, 140)

# CMYK Colors
translate(0, 140)
marker(140)
nostroke()
text("CMYK Colors", 20, 165)
cmykColors(140, 140)


# Text
translate(0, 140)
marker(140)
nostroke()
text("Basic text", 20, 165)
basictext(140, 165)     

# Aligned Text
translate(0, 140)
marker(140)
text("Aligned text", 20, 165)
alignedtext(140, 165)

# Rotated Text
translate(0, 140)
marker(140)
nostroke()
text("Rotated text", 20, 165)
with rotate(45):
    basictext(140, 165)

# Text blocks
translate(0, 140)
marker(140)
nostroke()
text("Text blocks", 20, 165)
textblock(140, 165)

# Text blocks
translate(0, 140)
marker(140)
nostroke()
text("Rotated text blocks", 20, 165)
with rotate(45):
    textblock(140, 165)


# Outlined text
translate(0, 140)
marker(140)
text("Outlined text", 20, 165)
with font(48), stroke(.5), fill('orange','cyan'):
    text("hamburgefonstiv", 140, 165, outline=True)

# Images
translate(0, 140)
marker(140)
text("Images", 20, 165)
images(140,165)


# classic Paths api
translate(0, 140)
marker(140)
stroke(.75)
text("Paths", 20, 165)
beginpath(165, 140)
lineto(140, 200)
curveto(160, 250, 160, 200, 190, 200)
p = endpath().copy()

stroke(0)
nofill()
sw = strokewidth()
strokewidth(2)
push()
translate(60,0)
for pt in p:
    pt.x += 60
    pt.ctrl1.x += 60
    pt.ctrl2.x += 60
drawpath(p)
pop()

# new Paths api
with transform():
    translate(120,0)
    with bezier(165, 140, strokewidth=4, stroke=.8) as p:
        lineto(140, 200)
        curveto(160, 250, 160, 200, 190, 200)
    
    p = p.copy()
    translate(60,0)
    for pt in p:
        pt.x += 60
        pt.ctrl1.x += 60
        pt.ctrl2.x += 60
    bezier(p, stroke=None, fill='red')
    bezier(p, strokewidth=2, stroke='#a00')
    
strokewidth(sw)
