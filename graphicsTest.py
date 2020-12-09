from my_cmu_112_graphics import *
from fighter import *

def appStarted(app):
    # Background Image found on https://entertainment.ie/gaming/pics-heres-the-real-life-locations-of-street-fighter-iis-stages-277425/
    app.background = app.loadImage("https://img.resized.co/entertainment/eyJkYXRhIjoie1widXJsXCI6XCJodHRwOlxcXC9cXFwvczMtZXUtd2VzdC0xLmFtYXpvbmF3cy5jb21cXFwvZW50ZXJ0YWlubWVudGllXFxcL3N0b3JhZ2VcXFwvaW1hZ2VzX2NvbnRlbnRcXFwvcmVjdGFuZ2xlXFxcLzYyMHgzNzJcXFwvdW5uYW1lZDYyMDE2MTEzMTgxOTcwNS5qcGdcIixcIndpZHRoXCI6NjQwLFwiaGVpZ2h0XCI6Mzg0LFwiZGVmYXVsdFwiOlwiaHR0cHM6XFxcL1xcXC9lbnRlcnRhaW5tZW50LmllXFxcL2ltYWdlc1xcXC9uby1pbWFnZS5wbmdcIn0iLCJoYXNoIjoiZDgzYjBmNzVhNmY5YWViMTRmMjM1MjQxOTBhMGI5NWIyZDE0NjY4OCJ9/unnamed620161131819705.jpg")
    app.background = ImageTk.PhotoImage(app.background)
    
    app.count = 0
    app.timerDelay = 1
    app.winner = None
    fighter.GRAVITY = -0.5 * app.timerDelay
    fighter.FLOOR = app.height - 20
    app.player1 = fighter(app.width*(1/3), "red")
    app.player2 = xbox(app.width*(2/3), 1, "blue")
    # app.player1 = AI(app.width/3, "red")
    # app.player2 = AI(app.width*(2/3), "blue")
    app.player1.opponent = app.player2
    app.player2.opponent = app.player1
    app.limbWidth = body.LW
    app.game = True

def keyPressed(app, event):
    if event.key == "w":
        app.player1.analogStick(("l_thumb_y", 1))

def timerFired(app):
    app.count += 1
    fighter.applyGravity()

    for i in range(len(fighter._registry)):
        fighter.threads[i] = threading.Thread(target=fighter._registry[i].getInput)
        fighter.threads[i].start()

    for i in range(len(fighter._registry)):
        fighter.threads[i].join()

    if app.count % 66 == 0:
        fighter.updateFrames()
        check4Winner(app)

def check4Winner(app):
    if app.player1.health <= 0:
        app.winner = "Player 2"
        app.game = False
    elif app.player2.health <= 0:
        app.winner = "Player 1"
        app.game = False

def drawPlayers(app, canvas):
    for player in fighter._registry:
        color = player.color
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

        # Draw the Torso
        # Done like this to allow for better animations in future
        canvas.create_polygon(player.body.hipL, player.body.shoulderL, 
                              player.body.shoulderR, player.body.hipR, 
                              fill=color, width=0)

        # Draw the Head
        x,y = player.body.head
        r = body.HR
        canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, width=0)

def healthColor(player):
    healthPercent = player.health / fighter.startingHealth
    if healthPercent < 0.2: return "red"
    elif healthPercent < 0.5: return "orange"
    elif healthPercent < 0.8: return "yellow"
    else: return "green"

def drawHealthBars(app, canvas):
    canvas.create_rectangle(0, 10, app.player1.health, 30,
                            fill=healthColor(app.player1))
    canvas.create_rectangle(app.width - app.player2.health, 10,
                            app.width, 30, fill=healthColor(app.player2))

def drawBackground(app, canvas):
    canvas.create_image(app.width/2, app.height/2,
                        image=app.background)

def redrawAll(app, canvas):
    if app.count % 66 > 0:
        return
    if app.game:
        app._canvas.delete(ALL)
        drawBackground(app, canvas)
        drawPlayers(app, canvas)
        drawHealthBars(app, canvas)
    else:
        canvas.create_text(app.width/2, app.height/2, text=f"{app.winner} Wins!",
                            font="ariel 36 bold",fill="white")
        
runApp(width=fighter.screenWidth, height=400)