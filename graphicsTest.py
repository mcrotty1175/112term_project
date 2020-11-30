from my_cmu_112_graphics import *
from fighter import *

def appStarted(app):
    app.count = 0
    app.timerDelay = 1
    fighter.GRAVITY = -.25
    fighter.FLOOR = app.height - 20
    app.player1 = fighter(app.width*(1/2), 0)
    
    app.limbWidth = body.LW

def timerFired(app):
    app.count += 1
    fighter.applyGravity()
    # print(app.player1.body)
    app.player1.move()

def drawTorso(app, canvas):
    color = app.player1.color
    x,y = app.player1.body.center
    w = body.THW
    h = body.THH
    canvas.create_rectangle(x-w, y-h, x+w, y+h, fill=color, width=0)

def drawHead(app, canvas):
    color = app.player1.color
    x,y = app.player1.body.head
    r = body.HR
    canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, width=0)

def drawArms(app, canvas):
    color = app.player1.color
    leftShoulderX, leftShoulderY = app.player1.body.shoulderL
    leftElbowX, leftElbowY = app.player1.body.elbowL
    leftHandX, lefthandY = app.player1.body.handL
    canvas.create_line(leftShoulderX, leftShoulderY,
                       leftElbowX, leftElbowY,
                       fill=color, width=app.limbWidth)
    canvas.create_line(leftElbowX, leftElbowY,
                       leftHandX, lefthandY,
                       fill=color, width=app.limbWidth)

    rightShoulderX, rightShoulderY = app.player1.body.shoulderR
    rightElbowX, rightElbowY = app.player1.body.elbowR
    rightHandX, rightHandY = app.player1.body.handR
    canvas.create_line(rightShoulderX, rightShoulderY,
                       rightElbowX, rightElbowY,
                       fill=color, width=app.limbWidth)
    canvas.create_line(rightElbowX, rightElbowY,
                       rightHandX, rightHandY,
                       fill=color, width=app.limbWidth)
    pass

def drawLegs(app, canvas):
    color = app.player1.color

    leftHipX, leftHipY = app.player1.body.hipL
    leftKneeX, leftKneeY = app.player1.body.kneeL
    leftHandX, leftFootY = app.player1.body.footL
    canvas.create_line(leftHipX, leftHipY,
                       leftKneeX, leftKneeY,
                       fill=color, width=app.limbWidth)
    canvas.create_line(leftKneeX, leftKneeY,
                       leftHandX, leftFootY,
                       fill=color, width=app.limbWidth)

    rightHipX, rightHipY = app.player1.body.hipR
    rightKneeX, rightKneeY = app.player1.body.kneeR
    rightHandX, rightFootY = app.player1.body.footR
    canvas.create_line(rightHipX, rightHipY,
                       rightKneeX, rightKneeY,
                       fill=color, width=app.limbWidth)
    canvas.create_line(rightKneeX, rightKneeY,
                       rightHandX, rightFootY,
                       fill=color, width=app.limbWidth)
    pass

def redrawAll(app, canvas):
    if app.count % 33 > 0:
        return
    app._canvas.delete(ALL)
    drawArms(app, canvas)
    drawLegs(app, canvas)
    drawTorso(app, canvas)
    drawHead(app, canvas)

runApp()