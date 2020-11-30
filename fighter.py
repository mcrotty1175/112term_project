from simpleQueue import simpleQueue
import X_input
import math

class fighter(object): 
    _registry = []
    GRAVITY = -0.5
    FLOOR = 300
    startingHealth = 200
    controls = {
        1: "self.health += 5",                                                # Dpad Up
        2: "self.health -= 5",                                                # Dpad Down
        3: "self.size -= 10",                                                 # Dpad Left
        4: "self.size += 10",                                                 # Dpad Right
        5: "pass",                                                            # Menu
        6: "pass",                                                            # View
        7: "pass",                                                            # L_Stick
        8: "pass",                                                            # R_Stick
        9: "self.color = 'red'",                                              # Left Bumper
        10: "self.color = 'blue'",                                            # Right Bumper
        13: "self.body.moveLimb('rightArm', 45, 90)",                         # A - Fast Punch
        14: "self.strongPunch()",                                             # B - Strong Punch
        15: "self.fastKick()",                                                # X - Fast Kick
        16: "self.strongKick()",                                              # Y - Strong Kick
        'left_trigger': "pass",                                        # Left Trigger Press
        'right_trigger': "pass",                                       # Right Trigger Press
        'l_thumb_x': "self.body.moveBody(2 * distance, 0)",                         # Left Stick X Positive
        'l_thumb_y': "self.jump()",                                             # Left Stick Y Positive 
        'r_thumb_x': "self.body.moveBody(5 * distance, 0)",                     # Right Stick X Positive
        'r_thumb_y': "pass",                                            # Right Stick Y Positive
        None:"pass"
    }

    # Magic Methods
    def __init__(self, startX, controller):
        fighter._registry.append(self)
        self.color = "red"
        self.x = startX
        self.body = body((startX, fighter.FLOOR))
        self.y = self.body.getHeight()
        self.health = fighter.startingHealth
        self.controller = X_input.sampleJoystick(controller)
        self.buttonLog = simpleQueue(5)
        self.frameTime = 0
        self.opponent = None

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
            if player.frameTime > 0:
                player.frameTime -= 0.03
            else:
                player.color = "red"

    # Class Methods
    def move(self):
        if self.getControllerInput():
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
    '''    
        def fastPunch(self):
            if self.frameTime <= 0:
                self.frameTime = 3
                self.color = "blue"
                if self.distance() <= (self.size + self.opponent.size):
                    self.opponent.health -= 3
            pass

        def strongPunch(self):
            if self.frameTime <= 0:
                self.frameTime = 7
                self.color = "green"
                if self.distance() <= (self.size + self.opponent.size):
                    self.opponent.health -= 10
            pass

        def fastKick(self):
            if self.frameTime <= 0:
                self.frameTime = 5
                self.color = "cyan"
                if self.distance() <= (self.size + self.opponent.size):
                    self.opponent.health -= 5
            pass

        def strongKick(self):
            if self.frameTime <= 0:
                self.frameTime += 10
                self.color = "black"
                if self.distance() <= (self.size + self.opponent.size):
                    self.opponent.health -= 15
            pass
    ''' 
    def jump(self):
        if self.canJump:
            self.body.moveBody(0, self.body.getHeight())
            self.canJump = False

    def getPos(self):
        return (self.x, self.y)
 
    def getControllerInput(self):
        data = next(self.controller)
        if data != None:
            if data[0] != None and data[0][2] == 1:
                self.buttonLog.join(data[0][1])
                print(data)
                return True
            elif data[1] != None:
                self.buttonLog.join((data[1][0], data[1][1]))
                return True
            else:
                return False

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
        self.createBody()
        self.moveBody(0, self.getHeight())

    def __str__(self):
        return f"Center point at {self.center}"

    def createBody(self):
        self.head = self.getPart(self.center, 0, (body.THH + body.HR))
        # Left Arm
        self.shoulderL = self.getPart(self.center, -1 * body.THW, body.THH)
        self.moveLimb("leftArm", 225, 135)
        # self.elbowL = self.getLimb(self.shoulderL, body.AL, 225)
        # self.handL = self.getLimb(self.elbowL, body.AL, 135)
        # Right Arm
        self.shoulderR = self.getPart(self.center, body.THW, body.THH)
        self.moveLimb("rightArm", 315, 45)
        # self.elbowR = self.getLimb(self.shoulderR, body.AL, 315)
        # self.handR = self.getLimb(self.elbowR, body.AL, 45)
        # Left Leg
        self.hipL = self.getPart(self.center, -1 * body.THW, -1* body.THH)
        self.moveLimb("leftLeg", 240, 270)
        # self.kneeL = self.getLimb(self.hipL, body.LL, 240)
        # self.footL = self.getLimb(self.kneeL, body.LL, 270)
        # Right Leg
        self.hipR = self.getPart(self.center, body.THW, -1* body.THH)
        self.moveLimb("rightLeg", 300, 270)
        # self.kneeR = self.getLimb(self.hipR, body.LL, 300)
        # self.footR = self.getLimb(self.kneeR, body.LL, 270)

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