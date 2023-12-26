
# 将指令str分割为op,dest和操作数组成的数组
def split_instruction(instruction):
    splited_instruction = instruction.split(" ")
    if len(splited_instruction) != 4:
            raise ValueError("错误的指令格式")
    return splited_instruction

# 读入指令过程
def read_and_update(input_file, output_file, rs, rb, rrs):
    cycle = 1
    last_cycle = 1
    index = 0
    last_output = ""
    with open(input_file) as f:
        for input in f.readlines():
            output = ""
            input = input.strip('\n')
            inst = split_instruction(input)
            rs.update(rrs, rb, cycle+1)
            rs.insert(inst, rrs, index, rb)
            rb.insert(inst, rrs, cycle+1)
            index += 1 
            output += rb.show()
            output += rs.show()
            output += rrs.show()
            if output != last_output:
                if last_output == "":
                    last_output = output
                    continue
                if last_cycle != cycle:
                    with open(output_file, "a+") as w:
                        w.write("cycle " + str(last_cycle) + "-" + str(cycle) + ": \n")
                        w.write(last_output + "\n")
                else:
                    with open(output_file, "a+") as w:
                        w.write("cycle " + str(cycle) + ": \n")
                        w.write(last_output + "\n")
            cycle += 1
            if output != last_output:
                last_cycle = cycle
            last_output = output
    return cycle, last_cycle, last_output # 返回读入指令完后的周期，和上次输出

# 后续指令更新过程
def update(output_file, rs, rb, rrs, cycle, last_cycle, last_output):
    while True:
        output = ""
        rs.update(rrs, rb, cycle+1)
        output += rb.show()
        output += rs.show()
        output += rrs.show()
        if output != last_output:
            if last_cycle != cycle:
                with open(output_file, "a+") as w:
                    w.write("cycle " + str(last_cycle) + "-" + str(cycle) + ": \n")
                    w.write(last_output + "\n")
            else:
                with open(output_file, "a+") as w:
                    w.write("cycle " + str(cycle) + ": \n")
                    w.write(last_output + "\n")
        cycle += 1
        if output != last_output:
            last_cycle = cycle
        last_output = output
        if rb.check():
            break
    return cycle, last_output

# 输出每条指令状态转变周期
def result(output_file, cycle, last_output, rb):
    with open(output_file, "a+") as w:
        w.write("cycle " + str(cycle) + ": \n")
        w.write(last_output + "\n")
        w.write(rb.show_result())

# 清空output文件
def init_output(output_file):
    with open(output_file, 'w') as f:
        f.write("")