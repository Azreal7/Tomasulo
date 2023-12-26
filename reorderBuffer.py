
class Entry:
    '''
    self.no:Entry序号
    self.buffer[0]:忙位
    self.buffer[1]:完整指令
    self.buffer[2]:指令状态
    self.buffer[3]:dest
    self.buffer[4]:value
    self.times:[Issue_time, Exec_time, WR_time, Commit_time]
    '''
    def __init__(self, no) -> None:
        self.no = no
        self.buffer = ['' for _ in range(5)]
        self.buffer[0] = 0
        self.times = [0, 0, 0, 0]

    def insert(self, input, rrs, cycle):
        self.buffer[0] = 1
        self.buffer[1] = str(input[0]) + " " + str(input[1]) + "," + str(input[2]) + "," + str(input[3])
        self.buffer[2] = "Issue"
        self.buffer[3] = input[1]
        self.buffer[4] = ""
        rrs.status[str(input[1])] = self.no
        self.times[0] = cycle # 记录issue时间
        if self.no == 1:
            self.times[0] = 1

    # 指令重排序缓存当前状态输出
    def show(self):
        output = ""
        if self.buffer[0] == 0:
            busy = "No"
        else :
            busy = "Yes"
        output += "entry" + str(self.no) + " : " + str(busy)
        for i in range(1, 5):
            output += "," + str(self.buffer[i])
        output += ";\n"
        return output
    
    # 指令各周期开始时间输出
    def show_result(self):
        res = ""
        res += self.buffer[1] + ":" + str(self.times[0]) + "," + str(self.times[1]) + "," + str(self.times[2]) + "," + str(self.times[3]) + ";\n"
        return res
    
    # 用来检测什么时候状态更改，记录，便于最后结果输出
    def check(self, no, cycle):
        self.times[no] = cycle

class ReorderBuffer:
    
    def __init__(self) -> None:
        self.index = 0
        self.entrys = [0 for _ in range(8)]
        for i in range(8):
            self.entrys[i] = Entry(i+1)
    
    # 指令重排序缓存当前状态输出
    def show(self):
        output = ""
        for i in range(8):
            output += self.entrys[i].show()
        return output

    def insert(self, input, rrs, cycle):
        self.entrys[self.index % 8].insert(input, rrs, cycle)
        self.index += 1

    # 检测是否所有程序都运行结束
    def check(self):
        for i in range(8):
            if self.entrys[i].buffer[0] == 1:
                return False
        return True
    
    # 指令各周期开始时间输出
    def show_result(self):
        res = ""
        for i in range(8):
            if self.entrys[i].times[0] == 0:
                break
            res += self.entrys[i].show_result()
        return res