
RS_name = ["Add1", "Add2", "Add3", "LD1", "LD2", "Mult1", "Mult2"]

class RRS:
    def __init__(self) -> None:
        self.cycle = 0
        self.status = {} # 占用情况
        self.busy = {} # 忙位
        self.value = {} # 值
        name = "F"
        for i in range(11):
            self.status[name+str(i)] = 0
            self.busy[name+str(i)] = 0
            self.value[name+str(i)] = 0


    def is_available(self, name, rb):
        return self.busy[name] != 1 or (self.busy[name] == 1 and rb.entrys[self.status[name]-1].buffer[4] != '')
    
    def show(self):
        output = ""
        name = "F"
        output += "Reorder:"
        for i in range(11):
            output += name+str(i)+": "
            if self.status[name+str(i)] != 0:
                output += str(self.status[name+str(i)])+";"
            else:
                output += ';'
        output += "\n"
        output += "Busy:"
        for i in range(11):
            output += name+str(i)+": "
            if self.busy[name+str(i)] == 1:
                output += "Yes;"
            else:
                output += "No;"
        output += "\n"
        return output