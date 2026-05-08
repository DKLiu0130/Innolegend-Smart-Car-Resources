import sensor
import time
import gc
import ml
from pyb import UART, LED, Pin
import uos

from LED import LED_Control
from logger import write_log
from UART import PacketParser
from algorithm import detect_and_sort_numbers

# --------------------------------------
# 串口配置 - OpenMV使用pyb.UART
uart1 = UART(1, 115200, timeout_char=1000)  # UART1用于与STM32通信

# 用一个类管理串口
parser1 = PacketParser(uart1)

# ----------------------------------------
# 摄像头配置
sensor.reset()                      # 复位和初始化摄像头
sensor.set_pixformat(sensor.GRAYSCALE)  # 与训练保持一致（如您的模型为灰度）
sensor.set_framesize(sensor.QVGA)   # QVGA (320 x 240)
sensor.set_windowing((240, 240))    # 240x240窗口适配FOMO输入
sensor.skip_frames(time=2000)       # 等待设置生效
sensor.set_auto_gain(False)         # 关闭自动增益
sensor.set_auto_whitebal(False)     # 关闭白平衡

# ----------------------------------------
# AI 设置 - 加载训练好的TFLite模型（按FOMO建议）
try:
    load_to_fb = uos.stat('trained.tflite')[6] > (gc.mem_free() - (64*1024))
    model = ml.Model('trained.tflite', load_to_fb=load_to_fb)
    write_log('模型加载成功')
except Exception as e:
    write_log('模型加载失败: ' + str(e))
    model = None

# ----------------------------------------
# 启动完成后闪烁表示
for i in range(5):
    LED_Control(i)
    time.sleep_ms(200)

def main():
    global model, sensor, parser1
    target = None
    
    if model is None:
        write_log('模型未加载，程序退出')
        return
    
    while True:
        gc.collect()
        
        if parser1.uart_read():
            LED_Control(1)  # 读到数据，亮红灯
            data = parser1.data
            write_log('接收到数据: ' + str(data))

            if data == 0x1:
                write_log('开始获取目标数字')
                numbers = detect_and_sort_numbers(10, 1, sensor, model)
                write_log('检测到的数字: ' + str(numbers))

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
                write_log('进入路口2')
                numbers = detect_and_sort_numbers(10, 2, sensor, model)
                write_log('检测到的数字: ' + str(numbers))

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
                write_log('进入路口3')
                numbers = detect_and_sort_numbers(10, 4, sensor, model)

                if len(numbers) != 4:
                    continue
                write_log('检测到的数字: ' + str(numbers))

                if target in numbers:
                    if target in numbers[0:2]:
                        parser1.uart_write(0x02)
                    else:
                        parser1.uart_write(0x04)

            elif data == 0x08:
                write_log('进入路口4')
                numbers = detect_and_sort_numbers(10, 2, sensor, model)
                write_log('检测到的数字: ' + str(numbers))

                if len(numbers) != 2:
                    continue

                if target in numbers:
                    if target == numbers[0]:
                        parser1.uart_write(0x02)
                    else:
                        parser1.uart_write(0x04)
                        
        LED_Control(0)  # 处理完成，熄灭红灯

if __name__ == '__main__':
    write_log('系统启动完成')
    try:
        main()
    except KeyboardInterrupt:
        write_log('系统被用户中断')
    except Exception as e:
        write_log('系统异常退出: ' + str(e))
    finally:
        write_log('系统退出，进行资源清理')
