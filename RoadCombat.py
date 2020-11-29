from my_cmu_112_graphics import *
from fighter import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# class StreetFighter(ModalApp):
#     def appStarted(app):
#         # app.splashScreenMode = SplashScreenMode()
#         app.gameMode = Battle()
#         # app.helpMode = HelpMode()
#         app.setActiveMode(app.gameMode)
#         app.timerDelay = 1


class Battle(App):
    def appStarted(app):
        app.count = 0
        app.timerDelay = 1
        fighter.FLOOR = app.height - 30
        fighter.GRAVITY = .25
        app.player1 = fighter(app.width*(1/3), 0)
        try:
            app.player2 = fighter(app.width*(2/3), 1)
            app.player1.opponent = app.player2
            app.player2.opponent = app.player1
        except Exception:
            pass
        pass
          
    def timerFired(app):
        app.count += 1
        app.movePlayers()
        if(app.count % 30 == 29): fighter.nextState()
        pass

    def movePlayers(app):
        fighter.updateFrames()
        fighter.applyGravity()
        for player in fighter._registry:
            player.move()

    def drawPlayers(app, canvas):
        for player in fighter._registry:
            x,y = player.getPos()
            r = player.size
            if player.crouch:
                r /= 2
                y += r
            color = player.color
            canvas.create_oval(x - r,y - r, x + r, y + r, fill=color)
            canvas.create_text(x,y, text=player.health, fill="white")
        pass

    def redrawAll(app, canvas):
        if app.count%33 >0:
            return
        app._canvas.delete(ALL)
        app.drawPlayers(canvas)
        # canvas.create_text(app.width/2, app.height/2, text=app.count)
        pass
Battle(width=SCREEN_WIDTH,height=SCREEN_HEIGHT)