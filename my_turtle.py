#ITT20-UkuKJ-kilpkonna graafika

# import tkinter as tk
import turtle


# https://github.com/donkirkby/live-py-plugin/blob/master/test/PySrc/tools/svg_turtle.py


scr = turtle.Screen()
scr.screensize(300,300)
scr.setup(300,300)
scr.title("Palju asju...")
scr.bgcolor('indigo')

def rist(px, py, kp, tv='orange',jv='brown'):
    t = turtle.Turtle()
    t.penup()
    t.setpos(px, py)
    t.pendown()
    
    t.pensize(2)
    t.speed(0)
    t.color(jv, tv)    
    t.begin_fill()
    for x in range(0,4):
        t.forward(kp)
        t.left(90)
        t.forward(kp)
        t.right(90)
        t.forward(kp)
        t.right(90)
    t.end_fill()
    t.hideturtle()

def kuusnurk(kp, tv='lightblue',jv='red'):
    t = turtle.Turtle()
    t.penup()
    t.setpos(0-int(kp/2), 0-kp)
    t.pendown()
    
    t.pensize(2)
    t.speed(0)
    t.color("black",tv)
    t.begin_fill()
    for x in range(0,6):
        t.forward(kp)
        t.left(120)
        t.pencolor(jv)
        t.forward(kp)
        
        t.penup()
        t.backward(kp)
        t.pendown()
        
        t.pencolor("black")
        t.right(60)
    t.color("black",tv)
    t.end_fill()
    t.hideturtle()

def ruut(kp, px, py, tv='yellow'):
    t = turtle.Turtle()
    t.penup()
    t.setpos(px, py)
    t.pendown()
    
    t.pensize(2)
    t.speed(0)
    t.color("black",tv)
    t.begin_fill()
    for a in range(4):
        t.forward(kp)
        t.left(90)
    t.end_fill()
    t.hideturtle()


ruut(300, -150, -150, 'yellow')
    
colors=['black', 'teal','cyan','orange','teal','cyan','orange','teal','cyan','orange','teal','cyan','orange','teal','cyan','orange','teal','cyan','orange','teal','cyan']

a=[0,1,0,-2,-3,-5,-6,-5] #muudab kaldrea alguspunkti
for x,iii in {1:5,2:7,3:8,4:8,5:8,6:8,7:5}.items(): #mitu risti real
    ii=1
    while ii < iii:
        i = ii + a[x]
        rist( (i*25)+50-(x*25), 350-(i*50)-(x*75),   25, colors[ii]) # *x25 *y50
        ii += 1

kuusnurk(120, tv='blue')
kuusnurk(80, tv='teal')
kuusnurk(50, tv='cyan')
kuusnurk(30)
scr.getcanvas().postscript(file='my_turtle.ps')
turtle.exitonclick()
