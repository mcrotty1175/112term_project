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
        3: "self.size -= 10",                                                   # Dpad Left
        4: "self.size += 10",                                                   # Dpad Right
        5: "pass",                                                              # Menu
        6: "pass",                                                              # View
        7: "pass",                                                              # L_Stick
        8: "pass",                                                              # R_Stick
        9: "self.color = 'green'",                                              # Left Bumper
        10: "self.color = 'pink'",                                              # Right Bumper
        13: "self.nextState = 'fastPunch1'",                                    # A - Fast Punch
        14: "self.nextState = 'fastPunch1'",                                    # B - Strong Punch
        15: "self.nextState = 'fastPunch1'",                                    # X - Fast Kick
        16: "self.nextState = 'fastPunch1'",                                    # Y - Strong Kick
        'left_trigger': "pass",                                                 # Left Trigger Press
        'right_trigger': "pass",                                                # Right Trigger Press
        'l_thumb_x': "self.body.moveBody(2 * distance, 0)",                     # Left Stick X Positive
        'l_thumb_y': "self.jump()",                                             # Left Stick Y Positive 
        'r_thumb_x': "self.body.moveBody(5 * distance, 0)",                     # Right Stick X Positive
        'r_thumb_y': "pass",                                                    # Right Stick Y Positive
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
        self.buttonLog = simpleQueue(5)
        self.frameTime = 0
        self.currentState = "idle1"
        self.nextState = "idle1"
        self.opponent = None
        self.states = {
            "idleStates":["idle1"],
            "fastPunchStates":["fastPunch1", "fastPunch2", "fastPunch3"],
            "strongPunchStates":["strongPunch1", "strongPunch2", "strongPunch3",
                                "strongPunch4", "strongPunch5"],
            "fastKickStages":["fastKick1", "fastKick2",
                            "fastKick2", "fastKick4"],
            "strongPunchStates":["strongKick1", "strongKick2", "strongKick3",
                                "strongKick4", "strongKick5", "strongKick6"],
            "crouchStates":["crouch"],
        }
    # Static Methods
    @staticmethod
    def applyGravity():
        for player in fighter._registry:
            if player.body.center[1] + player.body.getHeight() < fighter.FLOOR:
                player.body.moveBody(0, fighter.GRAVITY)
            else:
                player.canJump = True
        pass

    @staticmethod
    def updateFrames():
        for player in fighter._registry:
            # if player.getControllerInput():
            #     command = player.buttonLog.getLastElement()
            #     player.nextState = player.getNextState(command)
            # else:
                exec(f"player.{player.currentState}()")
                player.currentState = player.nextState
                player.nextState = player.getNextState()

    # Class Methods
    def getNextState(self, command=None):
        if self.currentState == "gameOver": return
        elif command == None:
            try:
                for key in self.states:
                    if self.currentState in self.states[key]:
                        animation = self.states[key]
                        return animation[animation.index(self.currentState) + 1]
            except IndexError:
                return "idle1"
        else: return "idle1"
            

    def move(self):
        command = self.buttonLog.getLastElement()
        if isinstance(command, int):
            exec(fighter.controls[command])
        elif isinstance(command, tuple):
            distance = command[1]
            exec(fighter.controls[command[0]])

    def distance(self):
        x0, y0 = self.getPos()
        x1, y1 = self.opponent.getPos()
        return ((x1 - x0)**2 + (y1 - y0)**2)**(0.5)

    def duck(self):
        self.crouch = True

    def idle1(self):
        # Head
        self.body.head = self.body.getPart(self.body.center, 0, (body.THH + body.HR))
        # Left Arm
        self.body.shoulderL = self.body.getPart(self.body.center, -1 * body.THW, body.THH)
        self.body.moveLimb("leftArm", 225, 135)
        # Right Arm
        self.body.shoulderR = self.body.getPart(self.body.center, body.THW, body.THH)
        self.body.moveLimb("rightArm", 315, 45)
        # Left Leg
        self.body.hipL = self.body.getPart(self.body.center, -1 * body.THW, -1* body.THH)
        self.body.moveLimb("leftLeg", 240, 270)
        # Right Leg
        self.body.hipR = self.body.getPart(self.body.center, body.THW, -1* body.THH)
        self.body.moveLimb("rightLeg", 300, 270)
        
    def idle2(self):
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

    def fastPunch1(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftArm", 210, 150)
        else:
            self.body.moveLimb("rightArm", -30, 30)

    def fastPunch2(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftArm", 180, 180)
        else:
            self.body.moveLimb("rightArm", 0, 0)
        
    def fastPunch3(self):
        if self.opponent.body.center < self.body.center:
            self.body.moveLimb("leftArm", 195, 165)
        else:
            self.body.moveLimb("rightArm", -15, 15)

    def jump(self):
        if self.canJump:
            self.body.moveBody(0, self.body.getHeight())
            self.canJump = False

    def getPos(self):
        return (self.x, self.y)
 
    def getControllerInput(self):
        if self.controller != None:
            data = next(self.controller)
            if data != None:
                if data[0] != None and data[0][2] == 1:
                    self.buttonLog.join(data[0][1])
                elif data[1] != None:
                    self.buttonLog.join((data[1][0], data[1][1]))
                self.move()

class body(object):
    THW = 10                                                                    # TORSO_HALF_WIDTH
    THH = 20                                                                    # TORSO_HALF_HEIGHT
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