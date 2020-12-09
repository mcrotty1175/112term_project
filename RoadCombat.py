from my_cmu_112_graphics import *
from fighter import *

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360


class MyModalApp(ModalApp):
    def appStarted(app):
        # Set Up App
        app.splashScreen = SplashScreen()
        app.colorSelect = ColorSelect()
        app.gameMode = Battle()
        app.helpMode = Help()
        app.timerDelay = 1

        fighter.screenWidth = app.width
        fighter.screenHeight = app.height
        app.colors = ["red", "green", "blue", "yellow", "cyan", "magenta"]

        app.colorPlayer1 = app.colorPlayer2 = random.sample(app.colors, 1)
        while app.colorPlayer2 == app.colorPlayer1:
            app.colorPlayer2 = random.sample(app.colors, 1)

        app.player1 = AI(app.width/3, app.colorPlayer1)
        app.player2 = AI(app.width*(2/3), app.colorPlayer2)
        # Keep this at the end
        app.setActiveMode(app.splashScreen)

class SplashScreen(Mode):
    def appStarted(mode):
        mode.count = 0
        mode.timerDelay = 1
        fighter.GRAVITY = -0.5 * mode.timerDelay
        fighter.FLOOR = mode.height - 20
        mode.app.player1.opponent = mode.app.player2
        mode.app.player2.opponent = mode.app.player1
        mode.limbWidth = body.LW
        mode.background = mode.loadImage("https://img.resized.co/entertainment/eyJkYXRhIjoie1widXJsXCI6XCJodHRwOlxcXC9cXFwvczMtZXUtd2VzdC0xLmFtYXpvbmF3cy5jb21cXFwvZW50ZXJ0YWlubWVudGllXFxcL3N0b3JhZ2VcXFwvaW1hZ2VzX2NvbnRlbnRcXFwvcmVjdGFuZ2xlXFxcLzYyMHgzNzJcXFwvdW5uYW1lZDYyMDE2MTEzMTgxOTcwNS5qcGdcIixcIndpZHRoXCI6NjQwLFwiaGVpZ2h0XCI6Mzg0LFwiZGVmYXVsdFwiOlwiaHR0cHM6XFxcL1xcXC9lbnRlcnRhaW5tZW50LmllXFxcL2ltYWdlc1xcXC9uby1pbWFnZS5wbmdcIn0iLCJoYXNoIjoiZDgzYjBmNzVhNmY5YWViMTRmMjM1MjQxOTBhMGI5NWIyZDE0NjY4OCJ9/unnamed620161131819705.jpg")
        mode.background = ImageTk.PhotoImage(mode.background)
    
    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.colorSelect)

    def timerFired(mode):
        mode.count += 1
        fighter.applyGravity()

        for i in range(len(fighter._registry)):
            fighter.threads[i] = threading.Thread(target=fighter._registry[i].getInput)
            fighter.threads[i].start()

        for i in range(len(fighter._registry)):
            fighter.threads[i].join()

        if mode.count % 66 == 0:
            fighter.updateFrames()

    def drawPlayers(mode, canvas):
        for player in fighter._registry:
            color = player.color
            # Draw Left Arm
            leftShoulderX, leftShoulderY = player.body.shoulderL
            leftElbowX, leftElbowY = player.body.elbowL
            leftHandX, lefthandY = player.body.handL
            canvas.create_line(leftShoulderX, leftShoulderY,
                            leftElbowX, leftElbowY,
                            fill=color, width=mode.limbWidth)
            canvas.create_line(leftElbowX, leftElbowY,
                            leftHandX, lefthandY,
                            fill=color, width=mode.limbWidth)

            # Draw Right Arm
            rightShoulderX, rightShoulderY = player.body.shoulderR
            rightElbowX, rightElbowY = player.body.elbowR
            rightHandX, rightHandY = player.body.handR
            canvas.create_line(rightShoulderX, rightShoulderY,
                            rightElbowX, rightElbowY,
                            fill=color, width=mode.limbWidth)
            canvas.create_line(rightElbowX, rightElbowY,
                            rightHandX, rightHandY,
                            fill=color, width=mode.limbWidth)

            # Draw Left Leg
            leftHipX, leftHipY = player.body.hipL
            leftKneeX, leftKneeY = player.body.kneeL
            leftHandX, leftFootY = player.body.footL
            canvas.create_line(leftHipX, leftHipY,
                            leftKneeX, leftKneeY,
                            fill=color, width=mode.limbWidth)
            canvas.create_line(leftKneeX, leftKneeY,
                            leftHandX, leftFootY,
                            fill=color, width=mode.limbWidth)

            # Draw Right Leg
            rightHipX, rightHipY = player.body.hipR
            rightKneeX, rightKneeY = player.body.kneeR
            rightHandX, rightFootY = player.body.footR
            canvas.create_line(rightHipX, rightHipY,
                            rightKneeX, rightKneeY,
                            fill=color, width=mode.limbWidth)
            canvas.create_line(rightKneeX, rightKneeY,
                            rightHandX, rightFootY,
                            fill=color, width=mode.limbWidth)

            # Draw the Torso
            # Done like this to allow for better animations in future
            canvas.create_polygon(player.body.shoulderL, player.body.shoulderR, 
                                player.body.hipR, player.body.hipL, 
                                fill=color, width=0)

            # Draw the Head
            x,y = player.body.head
            r = body.HR
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, width=0)
    
    def drawBackground(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2,
                            image=mode.background)

    def redrawAll(mode, canvas):
        if mode.count % 66 > 0:
            return
        mode.app._canvas.delete(ALL)
        mode.drawBackground(canvas)
        mode.drawPlayers(canvas)

class ColorSelect(Mode):
    def appStarted(mode):
        fighter._registry = []
        fighter.threads = []
        p1Select = True
        p2Select = False

    def drawColors(mode, canvas):
        pass

    def redrawAll(mode, canvas):
        canvas.crea

class Battle(Mode):
    def appStarted(mode):
        # Background Image found on https://entertainment.ie/gaming/pics-heres-the-real-life-locations-of-street-fighter-iis-stages-277425/
        mode.background = mode.loadImage("https://img.resized.co/entertainment/eyJkYXRhIjoie1widXJsXCI6XCJodHRwOlxcXC9cXFwvczMtZXUtd2VzdC0xLmFtYXpvbmF3cy5jb21cXFwvZW50ZXJ0YWlubWVudGllXFxcL3N0b3JhZ2VcXFwvaW1hZ2VzX2NvbnRlbnRcXFwvcmVjdGFuZ2xlXFxcLzYyMHgzNzJcXFwvdW5uYW1lZDYyMDE2MTEzMTgxOTcwNS5qcGdcIixcIndpZHRoXCI6NjQwLFwiaGVpZ2h0XCI6Mzg0LFwiZGVmYXVsdFwiOlwiaHR0cHM6XFxcL1xcXC9lbnRlcnRhaW5tZW50LmllXFxcL2ltYWdlc1xcXC9uby1pbWFnZS5wbmdcIn0iLCJoYXNoIjoiZDgzYjBmNzVhNmY5YWViMTRmMjM1MjQxOTBhMGI5NWIyZDE0NjY4OCJ9/unnamed620161131819705.jpg")
        mode.background = ImageTk.PhotoImage(mode.background)
        
        mode.count = 0
        mode.timerDelay = 1
        mode.winner = None
        fighter.GRAVITY = -0.5 * mode.timerDelay
        fighter.FLOOR = mode.height - 20
        mode.app.player1.opponent = mode.app.player2
        mode.app.player2.opponent = mode.app.player1
        mode.limbWidth = body.LW
        mode.game = True

    def timerFired(mode):
        mode.count += 1
        fighter.applyGravity()

        for i in range(len(fighter._registry)):
            fighter.threads[i] = threading.Thread(target=fighter._registry[i].getInput)
            fighter.threads[i].start()

        for i in range(len(fighter._registry)):
            fighter.threads[i].join()

        if mode.count % 66 == 0:
            fighter.updateFrames()
            mode.check4Winner()

    def check4Winner(mode):
        if mode.player1.health <= 0:
            mode.winner = "Player 2"
            mode.game = False
        elif mode.player2.health <= 0:
            mode.winner = "Player 1"
            mode.game = False

    def drawPlayers(mode, canvas):
        for player in fighter._registry:
            color = player.color
            # Draw Left Arm
            leftShoulderX, leftShoulderY = player.body.shoulderL
            leftElbowX, leftElbowY = player.body.elbowL
            leftHandX, lefthandY = player.body.handL
            canvas.create_line(leftShoulderX, leftShoulderY,
                            leftElbowX, leftElbowY,
                            fill=color, width=mode.limbWidth)
            canvas.create_line(leftElbowX, leftElbowY,
                            leftHandX, lefthandY,
                            fill=color, width=mode.limbWidth)

            # Draw Right Arm
            rightShoulderX, rightShoulderY = player.body.shoulderR
            rightElbowX, rightElbowY = player.body.elbowR
            rightHandX, rightHandY = player.body.handR
            canvas.create_line(rightShoulderX, rightShoulderY,
                            rightElbowX, rightElbowY,
                            fill=color, width=mode.limbWidth)
            canvas.create_line(rightElbowX, rightElbowY,
                            rightHandX, rightHandY,
                            fill=color, width=mode.limbWidth)

            # Draw Left Leg
            leftHipX, leftHipY = player.body.hipL
            leftKneeX, leftKneeY = player.body.kneeL
            leftHandX, leftFootY = player.body.footL
            canvas.create_line(leftHipX, leftHipY,
                            leftKneeX, leftKneeY,
                            fill=color, width=mode.limbWidth)
            canvas.create_line(leftKneeX, leftKneeY,
                            leftHandX, leftFootY,
                            fill=color, width=mode.limbWidth)

            # Draw Right Leg
            rightHipX, rightHipY = player.body.hipR
            rightKneeX, rightKneeY = player.body.kneeR
            rightHandX, rightFootY = player.body.footR
            canvas.create_line(rightHipX, rightHipY,
                            rightKneeX, rightKneeY,
                            fill=color, width=mode.limbWidth)
            canvas.create_line(rightKneeX, rightKneeY,
                            rightHandX, rightFootY,
                            fill=color, width=mode.limbWidth)

            # Draw the Torso
            # Done like this to allow for better animations in future
            canvas.create_polygon(player.body.shoulderL, player.body.shoulderR, 
                                player.body.hipR, player.body.hipL, 
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

    def drawHealthBars(mode, canvas):
        canvas.create_rectangle(0, 10, mode.player1.health, 30,
                                fill=healthColor(mode.player1))
        canvas.create_rectangle(mode.width - mode.app.player2.health, 10,
                                mode.width, 30, fill=healthColor(mode.app.player2))

    def drawBackground(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2,
                            image=mode.background)

    def redrawAll(mode, canvas):
        if mode.count % 66 > 0:
            return
        if mode.game:
            mode._canvas.delete(ALL)
            drawBackground(mode, canvas)
            drawPlayers(mode, canvas)
            drawHealthBars(mode, canvas)
        else:
            canvas.create_text(mode.width/2, mode.height/2, text=f"{mode.winner} Wins!",
                                font="ariel 36 bold",fill="white")

class Help(Mode):
    pass

class gameOver(Mode):
    pass

app = MyModalApp(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)