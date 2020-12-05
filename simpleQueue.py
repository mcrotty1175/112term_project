class simpleQueue(object):
    buttonMap = {
            1: "Up",
            2: "Down",
            3: "Left",
            4: "Right",
            5: "Menu",
            6: "View",
            7: "L_Stick",
            8: "R_Stick",
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
    def __init__(self, max, entities=[]):
        self.max = max
        self.list = entities

    def __hash__(self):
        result = 0
        for elem in self.list:
            result += elem
        return hash(result)

    def __eq__(self, other):
        for i in range(len(self.list)):
            if self.list[i] != other[i]:
                return False
        return True

    def __str__(self):
        if self.list == []:
            return "[]"
        else:
            result = f"[{simpleQueue.buttonMap[self.list[0]]}"
            for elem in self.list[1:]:
                result += ", " + str(simpleQueue.buttonMap[elem])
            result += "]"
            return result
    
    def __iter__(self):
        for elem in self.list:
            yield elem
    
    def __repr__(self):
        return f"simpleQueue({self.max}, {self.list})"

    def pop(self):
        return simpleQueue(self.max, self.list[1:])
    
    def popFirst(self):
        result = self.list[0]
        self.list = self.pop
        return result

    def join(self, elem):
        if len(self.list) < self.max:
            self.list.append(elem)
        else:
            temp = self.pop()
            temp.join(elem)
            self.list = temp.list

    def getLastElement(self):
        if self.list != []:
            return self.list[-1]

    def findCombos(self, combo):
        if len(self.list) < 2:
            return None
        elif self.list == combo:
            return self.list
        else:
            return self.pop().findCombos(combo)

