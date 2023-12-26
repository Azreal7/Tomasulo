import registerReslutStatus as regRS
import reservationStation as resS
import reorderBuffer as rB
import functions as func

input_file = "input1.txt"
output_file = "output1.txt"
rrs = regRS.RRS()
rs = resS.RS()
rb = rB.ReorderBuffer()

# 初始化output
func.init_output(output_file)

# 读入指令
cycle, last_cycle, last_output = func.read_and_update(input_file, output_file, rs, rb, rrs)
        
# 读完指令后的指令持续运行
cycle, last_output = func.update(output_file, rs, rb, rrs, cycle, last_cycle, last_output)

# 输出结果
func.result(output_file, cycle, last_output, rb)