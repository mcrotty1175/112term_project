from my_cmu_112_graphics import *
from fighter import *

def appStarted(app):
    app.count = 0
    app.timerDelay = 100
    fighter.GRAVITY = -1.5
    fighter.FLOOR = app.height - 20
    app.player1 = fighter(app.width*(1/3), 0, "red")
    # try:
    #     app.player2 = fighter(app.width*(2/3), 1, "blue")
    #     app.player1.opponent = app.player2
    #     app.player2.opponent = app.player1
    # except Exception:
    #     pass
    app.limbWidth = body.LW

def timerFired(app):
    app.count += 1
    fighter.applyGravity()
    for player in fighter._registry:
        player.getControllerInput()
    # if app.count % 66 > 0:
    fighter.updateFrames()

def drawPlayers(app, canvas):
    for player in fighter._registry:
        color = player.color

        # Draw the Torso
        x,y = player.body.center
        w = body.THW
        h = body.THH
        canvas.create_rectangle(x-w, y-h, x+w, y+h, fill=color, width=0)

        # Draw the Head
        x,y = player.body.head
        r = body.HR
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, width=0)

        # Draw Left Arm
        leftShoulderX, leftShoulderY = player.body.shoulderL
        leftElbowX, leftElbowY = player.body.elbowL
        leftHandX, lefthandY = player.body.handL
        canvas.create_line(leftShoulderX, leftShoulderY,
                        leftElbowX, leftElbowY,
                        fill=color, width=app.limbWidth)
        canvas.create_line(leftElbowX, leftElbowY,
                        leftHandX, lefthandY,
                        fill=color, width=app.limbWidth)

        # Draw Right Arm
        rightShoulderX, rightShoulderY = player.body.shoulderR
        rightElbowX, rightElbowY = player.body.elbowR
        rightHandX, rightHandY = player.body.handR
        canvas.create_line(rightShoulderX, rightShoulderY,
                        rightElbowX, rightElbowY,
                        fill=color, width=app.limbWidth)
        canvas.create_line(rightElbowX, rightElbowY,
                        rightHandX, rightHandY,
                        fill=color, width=app.limbWidth)

        # Draw Left Leg
        leftHipX, leftHipY = player.body.hipL
        leftKneeX, leftKneeY = player.body.kneeL
        leftHandX, leftFootY = player.body.footL
        canvas.create_line(leftHipX, leftHipY,
                        leftKneeX, leftKneeY,
                        fill=color, width=app.limbWidth)
        canvas.create_line(leftKneeX, leftKneeY,
                        leftHandX, leftFootY,
                        fill=color, width=app.limbWidth)

        # Draw Right Leg
        rightHipX, rightHipY = player.body.hipR
        rightKneeX, rightKneeY = player.body.kneeR
        rightHandX, rightFootY = player.body.footR
        canvas.create_line(rightHipX, rightHipY,
                        rightKneeX, rightKneeY,
                        fill=color, width=app.limbWidth)
        canvas.create_line(rightKneeX, rightKneeY,
                        rightHandX, rightFootY,
                        fill=color, width=app.limbWidth)


def redrawAll(app, canvas):
    # if app.count % 66 > 0:
    #     return
    app._canvas.delete(ALL)
    drawPlayers(app, canvas)

runApp(width=800, height=400)