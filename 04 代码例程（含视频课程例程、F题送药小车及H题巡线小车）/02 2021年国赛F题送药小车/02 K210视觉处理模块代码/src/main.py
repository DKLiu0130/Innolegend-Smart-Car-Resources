import sys
import os
import utime
import gc
import sensor
from fpioa_manager import fm
from machine import UART

from LED import LED_Control
from logger import write_log
from uart_data import PacketParser
from yolo import YOLO
from algorithm import detect_and_sort_numbers



# --------------------------------------

# 串口配置
fm.register(7, fm.fpioa.UART1_RX, force=True)
fm.register(6, fm.fpioa.UART1_TX, force=True)
fm.register(9, fm.fpioa.UART2_TX, force=True)
fm.register(8, fm.fpioa.UART2_RX, force=True)

#初始化串口
uart1 = UART(UART.UART1, 115200, read_buf_len=4096)
uart2 = UART(UART.UART2, 115200, read_buf_len=4096)

# 用一个类管理串口
parser1 = PacketParser(uart1)

# ----------------------------------------
# 摄像头配置

sensor.reset()                      # 复位和初始化摄像头，执行sensor.run(0)停止。
sensor.set_hmirror(1)
sensor.set_vflip(1)
sensor.set_pixformat(sensor.RGB565) # 设置像素格式为彩色 RGB565 (或灰色)
sensor.set_framesize(sensor.QVGA)   # 设置帧大小为 QVGA (224 x 224)
sensor.skip_frames(time = 2000)     # 等待设置生效
sensor.run(1)

# ----------------------------------------

# AI 设置
model = YOLO()

# ----------------------------------------

# 启动完成后闪烁表示

for i in range(5):
    LED_Control(i)
    utime.sleep_ms(200)


def main():
    global model, sensor, parser1
    target = None
    while True:
        gc.collect()
        if parser1.uart_read():
            LED_Control(1)  # 读到数据，亮红灯
            data = parser1.data
            write_log("接收到数据: " + str(data))

            if data == 0x1:
                write_log("开始获取目标数字")

                numbers = detect_and_sort_numbers(10, 1, sensor, model)

                write_log("检测到的数字: " + str(numbers))

                if len(numbers) == 0:
                    continue

                if len(numbers) == 1:
                    if numbers[0] == 1:
                        parser1.uart_write(0x02)
                    elif numbers[0] == 2:
                        parser1.uart_write(0x04)
                    else:
                        parser1.uart_write(0x01)

                target = numbers[0]

            elif data == 0x2:
                write_log("进入路口2")

                numbers = detect_and_sort_numbers(10, 2, sensor, model)

                write_log("检测到的数字: " + str(numbers))

                if len(numbers) != 2:
                    continue

                if target in numbers:
                    if target == numbers[0]:
                        parser1.uart_write(0x02)
                    else:
                        parser1.uart_write(0x04)
                else:
                    parser1.uart_write(0x01)

            elif data == 0x4:
                write_log("进入路口3")

                numbers = detect_and_sort_numbers(10, 4, sensor, model)

                if len(numbers) != 4:
                    continue
                write_log("检测到的数字: " + str(numbers))

                if target in numbers:
                    if target in numbers[0:2]:
                        parser1.uart_write(0x02)
                    else:
                        parser1.uart_write(0x04)

            elif data == 0x08:
                write_log("进入路口4")

                numbers = detect_and_sort_numbers(10, 2, sensor, model)

                write_log("检测到的数字: " + str(numbers))

                if len(numbers) != 2:
                    continue

                if target in numbers:
                    if target == numbers[0]:
                        parser1.uart_write(0x02)
                    else:
                        parser1.uart_write(0x04)
        LED_Control(-1)  # 处理完成，熄灭红灯
        
if __name__ == "__main__":
    write_log("系统启动完成")
    try:
        main()
    finally:
        write_log("系统退出，进行资源清理")
        model.cleanup()

