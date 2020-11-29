import X_input
import my_cmu_112_graphics
from simpleQueue import simpleQueue

def main():
    player1 = simpleQueue(5)
    controller0 = X_input.sampleJoystick(0)
    buttonMap = {
            1: "Up",
            2: "Down",
            3: "Left",
            4: "Right",
            5: None,
            6: None,
            7: None,
            8: None,
            9: "L_Bumper",
            10: "R_Bumper",
            11: None,
            12: None,
            13: "A",
            14: "B",
            15: "X",
            16: "Y",
            None:None
        }
    while True:
        p1 = next(controller0)
        if p1 != None:
            if p1[0] != None and p1[0][2] == 1:
                player1.join(buttonMap[p1[0][1]])
            if p1[1] != None:
                result = (p1[1][0], p1[1][1])
                player1.join(result)
                print(result)
            print(player1.getLastElement())


if __name__ == "__main__":
    main()
