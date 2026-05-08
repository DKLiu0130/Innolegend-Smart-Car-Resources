from fpioa_manager import fm
from machine import UART
import time

fm.register(9,fm.fpioa.UART1_RX,force = True)
fm.register(10,fm.fpioa.UART1_TX,force = True)

uart = UART(UART.UART1, 115200)

def parse_uart_data():
    if uart.any()>=3:
        frame = uart.read(3)
        if frame[0] == 0xFE and frame[2] ==0xFD:
            data = frame[1]
            print("成功接收指令包: [FE " + hex(data) + " FD]")
            return True

last_send_time = time.ticks_ms()
while True:
    parse_uart_data()
    if time.ticks_diff(time.ticks_ms(), last_send_time) > 1000:
        last_send_time = time.ticks_ms()  # 更新发送时间
        packet_to_send = bytearray([0xFE,0x01,0xFD])
        uart.write(packet_to_send)
