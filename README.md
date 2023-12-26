# Tomasulo
中山大学 计算机体系结构课程 Tomasulo算法实现

实现了带有reorderBuffer的Speculative Tomasulo算法。

文件结构：

- functions.py：整理主要输入、输出功能。
- registerResultStatus.py：负责存储寄存器状态，说明寄存器被哪个指令占用。
- reorderBuffer.py：负责存储指令状态，控制指令有效按序输出。
- reservationStation.py：保留站，负责跟踪指令间关系，控制指令何时执行。
- main.py：整合以上文件功能，同一进行输入输出。
- input.txt：指令输入文件
- output.txt：结果输出文件

有用的话麻烦给个star吧！

不建议抄袭代码！！！
