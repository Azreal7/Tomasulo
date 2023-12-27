
time_set = {
    "ADDD":2, "SUBD":2, "MULTD":10, "DIVD":20, "LD":2, "SD":2
}

class station:
    '''
    self.buffer[0]:忙位
    self.buffer[1]:op
    self.buffer[2/3]:vj/vk
    self.buffer[4/5]:qj/qk
    self.buffer[6]:dest
    self.time:本状态运行剩余时间
    '''
    def __init__(self) -> None:
        self.buffer = ['' for _ in range(7)]
        self.buffer[0] = 0
        self.time = 0

    def is_available(self):
        return self.buffer[0] == 0
    
    def insert(self, input, rrs, no, rb):
        self.no = no
        self.buffer[0] = 1
        self.buffer[1] = input[0]
        self.buffer[6] = input[1]
        # 将dest所占用寄存器忙位标1
        if self.buffer[6][0] == 'F':
            rrs.busy[str(self.buffer[6])] = 1
        # 装载需要1个周期，因此time初始化为1
        self.time = 1

        if input[0] == "LD" or input[0] == "SD":
            pass
        elif rrs.is_available(input[2], rb):
            if rrs.value[input[2]] != 0:
                self.buffer[2] = rrs.value[input[2]]
            else:
                self.buffer[2] = "Regs[" + str(input[2]) + "]"
        else:
            self.buffer[4] = rrs.status[input[2]]

        if input[0] == "LD" or input[0] == "SD":
            bias = '' # 如果vj是0，则直接输出Regs[vk]而非Regs[0+vk]
            if str(input[2]) != '0':
                bias = str(input[2])
            self.buffer[3] = "Mem[" + bias + "Regs[" + str(input[3]) + "]]"
        elif rrs.is_available(input[3], rb):
            if rrs.value[input[3]] != 0:
                self.buffer[3] = rrs.value[input[3]]
            else:
                self.buffer[3] = "Regs[" + str(input[3]) + "]"
        else:
            self.buffer[5] = rrs.status[input[3]]

    # 写更新
    def write_update(self, rss, rb, cycle, lock):
        if self.is_available():
            return
        if self.time > 0: self.time -= 1
        if self.time == 0:
            # Execute转Write Result
            if rb.entrys[self.no].buffer[2] == "Execute":
                # 根据不同op进行不同赋值操作
                if self.buffer[1] == "LD" or self.buffer[1] == "SD":
                    rb.entrys[self.no].buffer[4] = str(self.buffer[3])
                    rss.value[self.buffer[6]] = "#" + str(self.no + 1)
                elif self.buffer[1] == "ADDD":
                    rb.entrys[self.no].buffer[4] = str(self.buffer[2]) + "+" + str(self.buffer[3])
                elif self.buffer[1] == "SUBD":
                    rb.entrys[self.no].buffer[4] = str(self.buffer[2]) + "-" + str(self.buffer[3])
                elif self.buffer[1] == "DIVD":
                    rb.entrys[self.no].buffer[4] = str(self.buffer[2]) + "/" + str(self.buffer[3])
                elif self.buffer[1] == "MULTD":
                    rb.entrys[self.no].buffer[4] = str(self.buffer[2]) + "*" + str(self.buffer[3])
                # 状态转为Write Result
                rb.entrys[self.no].buffer[2] = "Write result"
                rb.entrys[self.no].check(1, cycle-1) # write result周期-1就是exec执行结束时间
                rb.entrys[self.no].check(2, cycle)
                self.time = 1
            # Write Result转结束
            elif rb.entrys[self.no].buffer[2] == "Write result":
                # 判断更新锁状态
                if lock == 1:
                    return
                # 判断顺序提交
                if self.no != 0:
                    if rb.entrys[self.no-1].buffer[2] != "Commit":
                        return
                rb.entrys[self.no].buffer[2] = "Commit"
                rb.entrys[self.no].buffer[0] = 0
                self.buffer[0] = 0
                rss.status[str(self.buffer[6])] = 0
                rss.value[str(self.buffer[6])] = "#" + str(self.no + 1)
                rss.busy[str(self.buffer[6])] = 0
                rb.entrys[self.no].check(3, cycle)
                lock = 1
        return lock # 返回更新锁状态

    # 读更新
    def read_update(self, rb, cycle):
        if self.is_available():
            return
        # Issue 转 Execute
        judge = 0 # 用于判断是否读到冒险的数据
        if self.time == 0:
            if rb.entrys[self.no].buffer[2] == "Issue":
                # 尝试读取冒险的数据
                if self.buffer[4] != '':
                    if rb.entrys[self.buffer[4]-1].buffer[4] != '':
                        self.buffer[2] = '#' + str(self.buffer[4])
                        self.buffer[4] = ''
                        judge = 1

                if self.buffer[5] != '':
                    if rb.entrys[self.buffer[5]-1].buffer[4] != '':
                        self.buffer[3] = '#' + str(self.buffer[5])
                        self.buffer[5] = ''
                        judge = 1

                if self.buffer[4] != '' or self.buffer[5] != '':
                    return # 判断是否需要等待
                if judge == 1:
                    return
                self.time = time_set[self.buffer[1]]
                rb.entrys[self.no].buffer[2] = "Execute"
    
    # 输出寄存器状态
    def show(self):
        output = ""
        if self.buffer[0] == 0:
            output += "No,,,,,;\n"
        else:
            output += "Yes,"
            for i in range(1, 7):
                output += str(self.buffer[i])
                if i < 6:
                    output += ','
            output += ";\n"
        return output

class RS:
    def __init__(self):
        self.Load1 = station()
        self.Load2 = station()
        self.Add1 = station()
        self.Add2 = station()
        self.Add3 = station()
        self.Mult1 = station()
        self.Mult2 = station()
        self.Mult3 = station()
        self.lock = 0 # 更新锁，防止多个station同时从write result更新为commit

    # 插入，成功返回1，失败返回0
    def insert(self, input, rrs, no, rb):
        type = input[0]
        if type == "LD" or type == "SD":
            if self.Load1.is_available():
                self.Load1.insert(input, rrs, no, rb)
            elif self.Load2.is_available():
                self.Load2.insert(input, rrs, no, rb)
            else:
                return -1
        elif type == "ADDD" or type == "SUBD":
            if self.Add1.is_available():
                self.Add1.insert(input, rrs, no, rb)
            elif self.Add2.is_available():
                self.Add2.insert(input, rrs, no, rb)
            elif self.Add3.is_available():
                self.Add3.insert(input, rrs, no, rb)
            else:
                return -1
        elif type == "DIVD" or type == "MULTD":
            if self.Mult1.is_available():
                self.Mult1.insert(input, rrs, no, rb)
            elif self.Mult2.is_available():
                self.Mult2.insert(input, rrs, no, rb)
            elif self.Mult3.is_available():
                self.Mult3.insert(input, rrs, no, rb)
            else:
                return -1
        return 1

    # 下个周期更新倒计时
    def update(self, rrs, rb, cycle):
        self.lock = self.Load2.write_update(rrs, rb, cycle, self.lock)
        self.lock = self.Mult3.write_update(rrs, rb, cycle, self.lock)
        self.lock = self.Load1.write_update(rrs, rb, cycle, self.lock)
        self.lock = self.Add1.write_update(rrs, rb, cycle, self.lock)
        self.lock = self.Add2.write_update(rrs, rb, cycle, self.lock)
        self.lock = self.Add3.write_update(rrs, rb, cycle, self.lock)
        self.lock = self.Mult1.write_update(rrs, rb, cycle, self.lock)
        self.lock = self.Mult2.write_update(rrs, rb, cycle, self.lock)
        self.Load1.read_update(rb, cycle)
        self.Load2.read_update(rb, cycle)
        self.Add1.read_update(rb, cycle)
        self.Add2.read_update(rb, cycle)
        self.Add3.read_update(rb, cycle)
        self.Mult1.read_update(rb, cycle)
        self.Mult2.read_update(rb, cycle)
        self.Mult3.read_update(rb, cycle)
        self.lock = 0

    # 打印保留站信息       
    def show(self):
        output = ""
        output += "Load1 :"
        output += self.Load1.show()
        output += "Load2 :"
        output += self.Load2.show()
        output += "Add1 :"
        output += self.Add1.show()
        output += "Add2 :"
        output += self.Add2.show()
        output += "Add3 :"
        output += self.Add3.show()
        output += "Mult1 :"
        output += self.Mult1.show()
        output += "Mult2 :"
        output += self.Mult2.show()
        output += "Mult3 :"
        output += self.Mult3.show()
        return output
