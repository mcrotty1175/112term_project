from simpleQueue import simpleQueue
import X_input
import math

class fighter(object): 
    _registry = []
    GRAVITY = -0.5
    FLOOR = 300
    startingHealth = 200
    controls = {
        1: "self.health += 5",                                                  # Dpad Up
        2: "self.health -= 5",                                                  # Dpad Down
        3: "self.dealDamage('handL', 50)",                                      # Dpad Left
        4: "self.dealDamage('handR', 50)",                                      # Dpad Right
        5: "pass",                                                              # Menu
        6: "pass",                                                              # View
        7: "pass",                                                              # L_Stick
        8: "pass",                                                              # R_Stick
        9: "self.color = 'green'",                                              # Left Bumper
        10: "self.color = 'pink'",                                              # Right Bumper
        13: "self.nextState = 'fastPunch1'",                                    # A - Fast Punch
        14: "self.nextState = 'strongPunch1'",                                  # B - Strong Punch
        15: "self.nextState = 'fastKick1'",                                     # X - Fast Kick
        16: "self.nextState = 'strongKick1'",                                   # Y - Strong Kick
        'left_trigger': "pass",                                                 # Left Trigger Press
        'right_trigger': "pass",                                                # Right Trigger Press
        'l_thumb_x': "self.body.moveBody(2 * distance, 0)",                     # Left Stick X Positive
        'l_thumb_y': "self.jump(distance)",                                     # Left Stick Y Positive 
        'r_thumb_x': "self.body.moveBody(5 * distance, 0)",                     # Right Stick X Positive
        'r_thumb_y': "self.nextState = 'crouch'",                               # Right Stick Y Positive
        None:"pass"
    }

    # Magic Methods
    def __init__(self, startX, controller, color="red"):
        fighter._registry.append(self)
        self.color = color
        self.x = startX
        self.body = body((startX, fighter.FLOOR))
        self.health = fighter.startingHealth
        try:
            self.controller = X_input.sampleJoystick(controller)
        except Exception:
            self.controller = None
        self.buttonLog = simpleQueue(10)
        self.frameTime = 0
        self.currentState = "idle1"
        self.nextState = "idle1"
        self.opponent = None
        self.combo = False
        self.possibleCombos = {
            "cheat": [1, 1, 2, 2, 3, 4, 3, 4, 14, 13],
            "heavyCombo":[2, 4, 14, 16],
            "quickCombo":[13, 13, 14]
        }
        self.states = {
            "idleStates":["idle1"],
            "fastPunchStates":["fastPunch1", "fastPunch2", "fastPunch3"],
            "strongPunchStates":["strongPunch1", "strongPunch2", "strongPunch3"],
            "fastKickStages":["fastKick1", "fastKick2","fastKick3", "fastKick4"],
            "strongKickStates":["strongKick1", "strongKick2", "strongKick3",
                                "strongKick4", "strongKick5", "strongKick6"],
            "crouchStates":["crouch"]
        }
    
    # Static Methods
    @staticmethod
    def applyGravity(): # Prevents double jumps and enforces gravity
        for player in fighter._registry:
            if player.body.center[1] + player.body.getHeight() < fighter.FLOOR:
                player.body.moveBody(0, fighter.GRAVITY)
            elif player.body.center[1] + player.body.getHeight() >= fighter.FLOOR:
                player.body.moveBody(0, player.getOptimalHeightDelta())
                player.canJump = True
        pass

    @staticmethod
    def updateFrames(): # Tells redrawAll how to draw each fighter
        for player in fighter._registry:
            exec(f"player.{player.currentState}()")
            player.currentState = player.nextState
            player.checkCombos()
            player.nextState = player.getNextState()

    # Class Methods
    def getOptimalHeightDelta(self):
        optimalHeight = fighter.FLOOR - self.body.getHeight()
        actualHeight = self.body.center[1]
        return  actualHeight - optimalHeight
    
    def checkCombos(self):
        for combo in self.possibleCombos:
            potential = self.buttonLog.findCombos(combo)
            if potential != None:
                self.combo = potential
                print(self.combo)
                break
        self.combo = None


    def getNextState(self): # Figures out what to draw next
        if self.currentState == "gameOver": return "gameOver"
        elif self.combo != None:
            return self.combo
        else: 
            try:
                for key in self.states:
                    if self.currentState in self.states[key]:
                        animation = self.states[key]
                        i = animation.index(self.currentState)
                        return animation[i + 1]
                return "idle1"
            except IndexError:
                return "idle1"
            
    def move(self): # Applies the player's next movement
        command = self.buttonLog.getLastElement()
        if isinstance(command, int):
            exec(fighter.controls[command])
        # elif isinstance(command, tuple):
        #     distance = command[1]
        #     exec(fighter.controls[command[0]])

    def distance(self, x0, y0, x1, y1):
        return ((x1 - x0)**2 + (y1 - y0)**2)**(0.5)

    def playerDistance(self): # Gets the distance between the players
        x0, y0 = self.getPos()
        x1, y1 = self.opponent.getPos()
        return self.distance(x0, y0, x1, y1)

    def crouch(self):
        self.body.moveLimb("leftLeg", 150, 270)
        self.body.moveLimb("rightLeg", 30, 270)
        dy = self.getOptimalHeightDelta()
        self.body.moveBody(0, dy)

    def idle1(self): # Default Idle Position
        # Head
        self.body.head = self.body.getPart(self.body.center, 0, (body.THH + body.HR))
        # Left Arm
        self.body.shoulderL = self.body.getPart(self.body.center, -1 * body.THW, body.THH)
        self.body.moveLimb("leftArm", 225, 105)
        # Right Arm
        self.body.shoulderR = self.body.getPart(self.body.center, body.THW, body.THH)
        self.body.moveLimb("rightArm", 315, 85)
        # Left Leg
        self.body.hipL = self.body.getPart(self.body.center, -1 * body.THW, -1* body.THH)
        self.body.moveLimb("leftLeg", 240, 270)
        # Right Leg
        self.body.hipR = self.body.getPart(self.body.center, body.THW, -1* body.THH)
        self.body.moveLimb("rightLeg", 300, 270)
        
    def idle2(self): # Secondary Idle Position (Need to change)
        # Head
        self.body.head = self.body.getPart(self.body.center, 0, (body.THH + body.HR))
        # Left Arm
        self.body.shoulderL = self.body.getPart(self.body.center, -1 * body.THW, body.THH)
        self.body.moveLimb("leftArm", 225, 135)
        # Right Arm
        self.body.shoulderR = self.body.getPart(self.body.center, body.THW, body.THH)
        self.body.moveLimb("rightArm", 0, 90)
        # Left Leg
        self.body.hipL = self.body.getPart(self.body.center, -1 * body.THW, -1* body.THH)
        self.body.moveLimb("leftLeg", 240, 270)
        # Right Leg
        self.body.hipR = self.body.getPart(self.body.center, body.THW, -1* body.THH)
        self.body.moveLimb("rightLeg", 300, 270)

    def dealDamage(self, appendage, baseDamage):
        x0, y0 = getattr(self.body, appendage)
        other = self.opponent.body
        if ((other.hipL[0] <= x0 <= other.hipR[0]) and
            (other.shoulderL[1] <= y0 <= other.hipR[1])):
            self.opponent.health -= baseDamage
        else:
            x1, y1 = other.head
            if self.distance(x0, y0, x1, y1) <= body.HR:
                self.opponent.health -= 1.5 * baseDamage
        if self.opponent.health <= 0:
            self.nextState = "gameOver"
            self.opponent.nextState = "gameOver"

    def gameOver(self):
        print("Game Over")

    def fastPunch1(self): # First frame of fast 
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftArm", 210, 150)
            self.dealDamage("handL", 4)
            
        else:
            self.body.moveLimb("rightArm", -30, 30)
            self.dealDamage("handR", 4)

    def fastPunch2(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftArm", 180, 180)
            self.dealDamage("handL", 4)
        else:
            self.body.moveLimb("rightArm", 0, 0)
            self.dealDamage("handR", 4)
    
    def fastPunch3(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftArm", 195, 165)
        else:
            self.body.moveLimb("rightArm", -15, 15)
            self.dealDamage("handR", 4)

    def strongPunch1(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("rightArm", 225, 135)
            self.dealDamage("handR", 4)
        else:
            self.body.moveLimb("leftArm", 315, 45)
            self.dealDamage("handL", 4)

    def strongPunch2(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("rightArm", 180, 90)
            self.dealDamage("elbowR", 10)
        else:
            self.body.moveLimb("leftArm", 0, 90)
            self.dealDamage("elbowL", 10)

    def strongPunch3(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("rightArm", 135, 105)
            self.dealDamage("handR", 4)
        else:
            self.body.moveLimb("leftArm", 45, 85)
            self.dealDamage("handL", 4)

    def fastKick1(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg", 215, 240)
        else:
            self.body.moveLimb("rightLeg", 320, 300)

    def fastKick2(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg", 200, 225)
        else:
            self.body.moveLimb("rightLeg", 340, 315)
    
    def fastKick3(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg", 180, 180)
        else:
            self.body.moveLimb("rightLeg", 0, 0)
    
    def fastKick4(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg", 200, 200)
        else:
            self.body.moveLimb("rightLeg", 340, 340)
    '''    
    def strongKick1(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg")
        else:
            self.body.moveLimb("leftLeg")

    def strongKick2(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg")
        else:
            self.body.moveLimb("leftLeg")

    def strongKick3(self): 
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg")
        else:
            self.body.moveLimb("leftLeg")

    def strongKick4(self): 
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg")
        else:
            self.body.moveLimb("leftLeg")

    def strongKick5(self): 
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg")
        else:
            self.body.moveLimb("leftLeg")

    def strongKick6(self): 
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftLeg")
        else:
            self.body.moveLimb("leftLeg")
    '''
    def jump(self):
        if self.canJump:
            self.body.moveBody(0, self.body.getHeight())
            self.canJump = False

    def getPos(self):
        return (self.x, self.y)

    def analogStick(self, intake):
        control, data = intake
        if control == 'left_trigger': pass
        elif control == 'right_trigger': pass
        elif control == 'l_thumb_x': 
            self.body.moveBody(2 * data, 0)
        elif control == 'l_thumb_y':
            if data >= 0: self.jump()
            else: self.nextState = "crouch"
        elif control == 'r_thumb_x':
            self.body.moveBody(5 * data, 0)
        elif control == 'r_thumb_y': pass

    def getInput(self):
        if self.controller != None:
            data = next(self.controller)
            if data != None:
                if data[0] != None and data[0][2] == 1:
                    self.buttonLog.join(data[0][1])
                    self.move()
                if data[1] != None:
                    # self.buttonLog.join((data[1][0], data[1][1]))
                    # self.move()
                    self.analogStick(data[1])
                    
                
class body(object):
    THW = 10                                                                    # TORSO_HALF_WIDTH
    THH = 25                                                                    # TORSO_HALF_HEIGHT
    HR = 20                                                                     # HEAD_RADIUS
    AL = 30                                                                     # ARM_LENGTH
    LL = 30                                                                     # LEG_LENGTH
    LW = 8                                                                      # LIMB_WIDTH
    bodyParts = ["head", "center",
                "shoulderL", "elbowL", "handL",
                "shoulderR", "elbowR", "handR",
                "hipL", "kneeL", "footL",
                "hipR", "kneeR", "footR"]
    limbs = {
        "leftArm":[AL, "shoulderL", "elbowL", "handL"],
        "rightArm":[AL, "shoulderR", "elbowR", "handR"],
        "leftLeg":[LL, "hipL", "kneeL", "footL"],
        "rightLeg":[LL, "hipR", "kneeR", "footR"]
    }


    def __init__(self, center):
        # Center
        self.center = center
         # Head
        self.head = self.getPart(self.center, 0, (body.THH + body.HR))
        # Left Arm
        self.shoulderL = self.getPart(self.center, -1 * body.THW, body.THH)
        self.moveLimb("leftArm", 225, 135)
        # Right Arm
        self.shoulderR = self.getPart(self.center, body.THW, body.THH)
        self.moveLimb("rightArm", 315, 45)
        # Left Leg
        self.hipL = self.getPart(self.center, -1 * body.THW, -1* body.THH)
        self.moveLimb("leftLeg", 240, 270)
        # Right Leg
        self.hipR = self.getPart(self.center, body.THW, -1* body.THH)
        self.moveLimb("rightLeg", 300, 270)
        self.moveBody(0, self.getHeight())

    def __str__(self):
        return f"Center point at {self.center}"

    def getPart(self, center, xOff, yOff):
        x, y = center
        x += xOff
        y -= yOff
        return (x,y)

    def getLimb(self, startPoint, length, angle=270):
        x,y = startPoint
        angleInRads = angle / 180 * math.pi 
        x += length * math.cos(angleInRads)
        y -= length * math.sin(angleInRads)
        return (x,y)

    def getJoint(self, joint):
        return getattr(self, joint)

    def getHeight(self):
        bottomFoot = max(self.footL[1], self.footR[1])
        return bottomFoot - self.center[1]

    def moveBody(self, dx, dy):
        for i in range(len(body.bodyParts)):
            x,y = getattr(self, body.bodyParts[i])
            x += dx
            y -= dy
            setattr(self, body.bodyParts[i], (x,y))
        pass
    
    def moveLimb(self, limb, theta1, theta2):
        limbParts = body.limbs[limb]
        length, socket, hinge, saddle = limbParts
        socketPos = getattr(self, socket)
        hingePos = self.getLimb(socketPos, length, theta1)
        setattr(self, hinge, hingePos)
        saddlePos = self.getLimb(hingePos, length, theta2)
        setattr(self, saddle, saddlePos)
        pass
    
    pass
