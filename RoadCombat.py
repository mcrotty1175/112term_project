# Run this file to get everything working
# Keyboards are now supported (Be sure to press and hold when moving)

# Background Image found on https://entertainment.ie/gaming/pics-heres-the-real-life-locations-of-street-fighter-iis-stages-277425/

from my_cmu_112_graphics import *
from fighter import *

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360

class MyModalApp(ModalApp):
    def appStarted(app):
        # Set Up App
        app.splashScreen = SplashScreen()
        app.colorSelectSingle = ColorSelectSingle()
        app.colorSelctMulti = ColorSelectMulti()
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
    
    def mousePressed(mode, event):
        if 3*mode.bH <= event.y <= 4*mode.bH:
            if mode.bW <= event.x <= 2*mode.bW:
                mode.app.setActiveMode(mode.app.colorSelectSingle)
            elif 3*mode.bW <= event.x <= 4*mode.bW:
                mode.app.setActiveMode(mode.app.colorSelctMulti)

    def timerFired(mode):
        mode.count += 1
        fighter.applyGravity()
        for player in fighter._registry:
            player.health = fighter.startingHealth
        
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
        canvas.create_line(0, fighter.FLOOR, mode.width, fighter.FLOOR)

    def drawGameModes(mode, canvas):
        mode.bW = 128 # buttonWidth
        mode.bH = 72 # buttonHeight

        canvas.create_rectangle(mode.bW, 3*mode.bH, 2*mode.bW, 4*mode.bH, fill="white")
        canvas.create_text(1.5*mode.bW, 3.5*mode.bH, text="Singleplayer")
        canvas.create_rectangle(3*mode.bW, 3*mode.bH, 4*mode.bW, 4*mode.bH, fill="white")
        canvas.create_text(3.5*mode.bW, 3.5*mode.bH, text="Multiplayer")

    def redrawAll(mode, canvas):
        if mode.count % 66 > 0:
            return
        mode.app._canvas.delete(ALL)
        mode.drawBackground(canvas)
        mode.drawPlayers(canvas)
        mode.drawGameModes(canvas)
        canvas.create_text(mode.app.width/2, mode.app.height/4, text="Road Combat",
                            font="arial 40 bold", fill="Black")

class ColorSelectSingle(Mode):
    def appStarted(mode):
        fighter._registry = []
        fighter.threads = []
        if X_input.checkControllers() > 0:
            mode.app.player1 = xbox(mode.app.width/3, 0, mode.app.colorPlayer1)
        else:
            mode.app.player1 = fighter(mode.app.width/3, mode.app.colorPlayer1)
        mode.app.player2 = AI(mode.app.width*(2/3), mode.app.colorPlayer2)

    def mousePressed(mode, event):
        if 120 <= event.y <= 200: 
            if 40 <= event.x <= 220: 
                mode.app.colorPlayer2 = mode.app.colorPlayer1 = "red"
                while mode.app.colorPlayer2 == mode.app.colorPlayer1:
                    mode.app.colorPlayer2 = random.sample(mode.app.colors, 1)
                mode.app.setActiveMode(Battle())
            if 230 <= event.x <= 410: 
                mode.app.colorPlayer2 = mode.app.colorPlayer1 = "green"
                while mode.app.colorPlayer2 == mode.app.colorPlayer1:
                    mode.app.colorPlayer2 = random.sample(mode.app.colors, 1)
                mode.app.setActiveMode(Battle())
            if 420 <= event.x <= 600: 
                mode.app.colorPlayer2 = mode.app.colorPlayer1 = "blue"
                while mode.app.colorPlayer2 == mode.app.colorPlayer1:
                    mode.app.colorPlayer2 = random.sample(mode.app.colors, 1)
                mode.app.setActiveMode(Battle())
        elif 220 <= event.y <= 300:
            if 40 <= event.x <= 220: 
                mode.app.colorPlayer2 = mode.app.colorPlayer1 = "cyan"
                while mode.app.colorPlayer2 == mode.app.colorPlayer1:
                    mode.app.colorPlayer2 = random.sample(mode.app.colors, 1)
                mode.app.setActiveMode(Battle())
            if 230 <= event.x <= 410: 
                mode.app.colorPlayer2 = mode.app.colorPlayer1 = "yellow"
                while mode.app.colorPlayer2 == mode.app.colorPlayer1:
                    mode.app.colorPlayer2 = random.sample(mode.app.colors, 1)
                mode.app.setActiveMode(Battle())
            if 420 <= event.x <= 600: 
                mode.app.colorPlayer2 = mode.app.colorPlayer1 = "magenta"
                while mode.app.colorPlayer2 == mode.app.colorPlayer1:
                    mode.app.colorPlayer2 = random.sample(mode.app.colors, 1)
                mode.app.setActiveMode(Battle())

    def drawColors(mode, canvas):
        canvas.create_rectangle(40, 120, 220, 200, fill="red")
        canvas.create_rectangle(230, 120, 410, 200, fill="green")
        canvas.create_rectangle(420, 120, 600, 200, fill="blue")
        canvas.create_rectangle(40, 220, 220, 300, fill="cyan")
        canvas.create_rectangle(230, 220, 410, 300, fill="yellow")
        canvas.create_rectangle(420, 220, 600, 300, fill="magenta")

    def redrawAll(mode, canvas):
        mode.app._canvas.delete(ALL)
        canvas.create_text(mode.app.width/2, 80, text="Select Your Color", font="arial 30 bold")
        mode.drawColors(canvas)

class ColorSelectMulti(Mode):
    def appStarted(mode):
        fighter._registry = []
        fighter.threads = []
        numControllers = X_input.checkControllers()
        if numControllers > 0:
            mode.app.player1 = xbox(mode.app.width/3, 0, mode.app.colorPlayer1)
            if numControllers > 1:
                mode.app.player2 = xbox(mode.app.width*(2/3), 1, mode.app.colorPlayer2)
            else:
                mode.app.player2 = fighter(mode.app.width*(2/3), mode.app.colorPlayer2)
        else:
            print("No controllers detected")
            mode.app.setActiveMode(mode.app.colorSelectSingle)
        mode.playerSelect = "P1"

    def mousePressed(mode, event):
        if mode.playerSelect == "P1":
            if 120 <= event.y <= 200: 
                if 40 <= event.x <= 220: 
                    mode.app.colorPlayer1 = "red"
                    mode.playerSelect = "P2"
                if 230 <= event.x <= 410: 
                    mode.app.colorPlayer1 = "green"
                    mode.playerSelect = "P2"
                if 420 <= event.x <= 600: 
                    mode.app.colorPlayer1 = "blue"
                    mode.playerSelect = "P2"
            elif 220 <= event.y <= 300:
                if 40 <= event.x <= 220: 
                    mode.app.colorPlayer1 = "cyan"
                    mode.playerSelect = "P2"
                if 230 <= event.x <= 410: 
                    mode.app.colorPlayer1 = "yellow"
                    mode.playerSelect = "P2"
                if 420 <= event.x <= 600: 
                    mode.app.colorPlayer1 = "magenta"
                    mode.playerSelect = "P2"
        else:
            if 120 <= event.y <= 200: 
                if 40 <= event.x <= 220: 
                    mode.app.colorPlayer2 = "red"
                    mode.app.setActiveMode(Battle())
                if 230 <= event.x <= 410: 
                    mode.app.colorPlayer2 = "green"
                    mode.app.setActiveMode(Battle())
                if 420 <= event.x <= 600: 
                    mode.app.colorPlayer2 = "blue"
                    mode.app.setActiveMode(Battle())
            elif 220 <= event.y <= 300:
                if 40 <= event.x <= 220: 
                    mode.app.colorPlayer2 = "cyan"
                    mode.app.setActiveMode(Battle())
                if 230 <= event.x <= 410: 
                    mode.app.colorPlayer2 = "yellow"
                    mode.app.setActiveMode(Battle())
                if 420 <= event.x <= 600: 
                    mode.app.colorPlayer2 = "magenta"
                    mode.app.setActiveMode(Battle())

    def drawColors(mode, canvas):
        canvas.create_rectangle(40, 120, 220, 200, fill="red")
        canvas.create_rectangle(230, 120, 410, 200, fill="green")
        canvas.create_rectangle(420, 120, 600, 200, fill="blue")
        canvas.create_rectangle(40, 220, 220, 300, fill="cyan")
        canvas.create_rectangle(230, 220, 410, 300, fill="yellow")
        canvas.create_rectangle(420, 220, 600, 300, fill="magenta")

    def redrawAll(mode, canvas):
        mode.app._canvas.delete(ALL)
        canvas.create_text(mode.app.width/2, 80, text=f"{mode.playerSelect} Select Your Color", font="arial 30 bold")
        mode.drawColors(canvas)

class Battle(Mode):
    def appStarted(mode):
        mode.background = mode.loadImage("https://img.resized.co/entertainment/eyJkYXRhIjoie1widXJsXCI6XCJodHRwOlxcXC9cXFwvczMtZXUtd2VzdC0xLmFtYXpvbmF3cy5jb21cXFwvZW50ZXJ0YWlubWVudGllXFxcL3N0b3JhZ2VcXFwvaW1hZ2VzX2NvbnRlbnRcXFwvcmVjdGFuZ2xlXFxcLzYyMHgzNzJcXFwvdW5uYW1lZDYyMDE2MTEzMTgxOTcwNS5qcGdcIixcIndpZHRoXCI6NjQwLFwiaGVpZ2h0XCI6Mzg0LFwiZGVmYXVsdFwiOlwiaHR0cHM6XFxcL1xcXC9lbnRlcnRhaW5tZW50LmllXFxcL2ltYWdlc1xcXC9uby1pbWFnZS5wbmdcIn0iLCJoYXNoIjoiZDgzYjBmNzVhNmY5YWViMTRmMjM1MjQxOTBhMGI5NWIyZDE0NjY4OCJ9/unnamed620161131819705.jpg")
        mode.background = ImageTk.PhotoImage(mode.background)
        
        mode.count = 0
        mode.timeLeft = 60
        mode.timerDelay = 1
        mode.winner = None
        fighter.GRAVITY = -0.5 * mode.timerDelay
        fighter.FLOOR = mode.height - 20

        for player in fighter._registry:
            player.health = fighter.startingHealth
        mode.app.player1.color = mode.app.colorPlayer1
        mode.app.player2.color = mode.app.colorPlayer2

        print(mode.app.player1.color, mode.app.player2.color)
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
        
        if mode.count % 1000 == 0:
            mode.timeLeft -= 1

    def keyPressed(mode, event):
        for player in fighter._registry:
            if not isinstance(player, AI) and not isinstance(player, xbox):
                if event.key in {"w", "Up"}:
                    player.analogStick(('l_thumb_y', 1))
                elif event.key in {"a", "Left"}:
                    player.analogStick(('l_thumb_x', -1))
                elif event.key in {"s", "Down"}:
                    player.analogStick(('l_thumb_y', -1))
                elif event.key in {"d", "Right"}:
                    player.analogStick(('l_thumb_x', 1))
                elif event.key == "j":
                    player.buttonLog.join(13)
                    player.move()
                elif event.key == "k":
                    player.buttonLog.join(14)
                    player.move()
                elif event.key == "n":
                    player.buttonLog.join(15)
                    player.move()
                elif event.key == "m":
                    player.buttonLog.join(16)
                    player.move()

    def check4Winner(mode):
        if mode.timeLeft > 0:
            if mode.app.player1.health <= 0:
                mode.winner = "Player 2"
                mode.game = False
            elif mode.app.player2.health <= 0:
                mode.winner = "Player 1"
                mode.game = False
        else:
            if mode.app.player1.health <= mode.app.player2.health:
                mode.winner = "Player 2"
                mode.game = False
            else:
                mode.winner = "Player 1"
                mode.game = False

    def mousePressed(mode, event):
        if not mode.game and ((mode.width/2 - 100) <= event.x <= (mode.width/2 + 100)):
            if mode.height*(2/3) - 20 <= event.y <= mode.height*(2/3) + 20:
                mode.app.setActiveMode(Battle())
            elif mode.height*(7/9) - 20 <= event.y <= mode.height*(7/9) + 20:
                mode.app.setActiveMode(mode.app.splashScreen)
            elif mode.height*(8/9) - 20 <= event.y <= mode.height*(8/9) + 20:
                mode.app.quit()

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

    def healthColor(mode, player):
        healthPercent = player.health / fighter.startingHealth
        if healthPercent < 0.2: return "red"
        elif healthPercent < 0.5: return "orange"
        elif healthPercent < 0.8: return "yellow"
        else: return "green"

    def drawHealthBars(mode, canvas):
        
        canvas.create_rectangle(0, 20, mode.app.player1.health, 40,
                                fill=mode.healthColor(mode.app.player1))
        canvas.create_text(mode.app.width/2, 40, text=str(mode.timeLeft),
                            fill="white", font="arial 40 bold")
        canvas.create_rectangle(mode.width - mode.app.player2.health, 20,
                                mode.width, 40, fill=mode.healthColor(mode.app.player2))

        canvas.create_text(20, 30, text="P1")
        canvas.create_text(mode.width - 20, 30, text="P2")

    def drawBackground(mode, canvas):
        canvas.create_image(mode.width/2, mode.height/2,
                            image=mode.background)

    def drawGameOver(mode, canvas):
        # Rematch
        canvas.create_rectangle((mode.width/2 - 100), mode.height*(2/3) - 20 ,
                                (mode.width/2 + 100), mode.height*(2/3) + 20,
                                 fill="lime")
        canvas.create_text(mode.width/2, mode.height*(2/3), text="Rematch?")
        # Title Screen
        canvas.create_rectangle((mode.width/2 - 100), mode.height*(7/9) - 20 ,
                                (mode.width/2 + 100), mode.height*(7/9) + 20,
                                 fill="lime")
        canvas.create_text(mode.width/2, mode.height*(7/9), text="Return to Title Screen")
        #Quit
        canvas.create_rectangle((mode.width/2 - 100), mode.height*(8/9) - 20 ,
                                (mode.width/2 + 100), mode.height*(8/9) + 20,
                                 fill="lime")
        canvas.create_text(mode.width/2, mode.height*(8/9), text="Quit")

    def redrawAll(mode, canvas):
        if mode.count % 66 > 0:
            return
        mode.app._canvas.delete(ALL)
        if mode.game:
            mode.drawBackground(canvas)
            mode.drawPlayers(canvas)
            mode.drawHealthBars(canvas)
        else:
            mode.drawGameOver(canvas)
            canvas.create_text(mode.width/2, mode.height/2, text=f"{mode.winner} Wins!",
                                font="ariel 40 bold",fill="black")

app = MyModalApp(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)