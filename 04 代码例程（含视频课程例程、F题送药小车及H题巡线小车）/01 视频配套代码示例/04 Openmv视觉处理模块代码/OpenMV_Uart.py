import pyb
import time

# 初始化串口3 (引脚 P4=TX, P5=RX)，波特率 115200
uart = pyb.UART(3, 115200)

def parse_uart_data():
    if uart.any()>=3:
        frame = uart.read(3)
        if frame[0] == 0xFE and frame[2] ==0xFD:
            data = frame[1]
            print(f"成功接收指令包: [FE {hex(data)} FD]")
            return True

last_send_time = time.ticks_ms()
while True:
    parse_uart_data()
    if time.ticks_diff(time.ticks_ms(), last_send_time) > 1000:
        last_send_time = time.ticks_ms()  # 更新发送时间
        packet_to_send = bytearray([0xFE,0x01,0xFD])
        uart.write(packet_to_send)
