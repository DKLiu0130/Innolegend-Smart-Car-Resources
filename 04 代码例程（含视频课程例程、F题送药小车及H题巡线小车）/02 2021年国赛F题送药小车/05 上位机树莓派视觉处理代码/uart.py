import serial
import time

# --- 配置参数 ---
# 串口设备文件，在鲁班猫上通常是 /dev/ttyS1, /dev/ttyS2 等
SERIAL_PORT = '/dev/ttyS1' 
# 波特率，必须与连接的设备设置一致
# 常见的波特率有 9600, 19200, 38400, 57600, 115200
BAUD_RATE = 115200


class PacketParser:
    """
    一个用于阻塞式解析特定格式串行数据包的类。
    - 初始化时接收端口号和波特率。
    - uart_read() 方法是阻塞的，直到接收到一个字节。
    - 完整的数据包解析需要外部调用三次 uart_read()。
    
    数据包格式: 0xFE (头) + 1字节数据 + 0xFD (尾)
    """
    # 定义状态常量
    STATE_WAIT_HEADER = 0
    STATE_WAIT_DATA = 1
    STATE_WAIT_FOOTER = 2

    # 定义协议字节
    PACKET_HEADER = 0xFE
    PACKET_FOOTER = 0xFD

    def __init__(self, port = SERIAL_PORT, baudrate = BAUD_RATE):
        """
        初始化解析器并打开指定的串口。
        :param port: 串口号 (例如: 'COM3' 或 '/dev/ttyUSB0')
        :param baudrate: 波特率 (例如: 9600)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        
        # 内部状态和数据
        self.state = self.STATE_WAIT_HEADER
        self.data = None

        try:
            # timeout=None 表示 read() 操作将无限期等待，直到读取到数据为止
            # 这实现了阻塞功能
            self.serial = serial.Serial(self.port, self.baudrate, timeout=None)
            print(f"成功打开串口: {self.port}，波特率: {self.baudrate}")
        except serial.SerialException as e:
            print(f"打开串口 {self.port} 失败: {e}")
            raise  # 将异常抛出，让调用者知道初始化失败

    def uart_read(self):
        """
        阻塞式地从串口读取一个字节，并根据状态机进行处理。
        该方法每次被调用，都会阻塞直到接收到一个字节。

        - 第一次调用（等待包头）: 返回 False
        - 第二次调用（等待数据）: 返回 False
        - 第三次调用（等待包尾）: 如果包尾正确，返回 True；否则返回 False
        
        :return: bool - 仅在第三次调用且包尾正确时返回 True。
        """
        # read(1) 将会一直阻塞，直到串口接收到1个字节的数据
        byte_in = self.serial.read(1)[0]
        
        # --- 状态机核心逻辑 ---

        # 状态 0: 等待包头 0xFE
        if self.state == self.STATE_WAIT_HEADER:
            if byte_in == self.PACKET_HEADER:
                # 收到正确的包头，状态转移到等待数据
                self.state = self.STATE_WAIT_DATA
            # 无论收到的是否是包头，第一次调用都返回 False
            return False

        # 状态 1: 等待数据字节
        elif self.state == self.STATE_WAIT_DATA:
            # 将收到的字节暂存到 self.data
            self.data = byte_in
            # 状态转移到等待包尾
            self.state = self.STATE_WAIT_FOOTER
            # 第二次调用返回 False
            return False

        # 状态 2: 等待包尾 0xFD
        elif self.state == self.STATE_WAIT_FOOTER:
            # 接收到第三个字节后，无论成功与否，都要重置状态机以备下次接收
            self.state = self.STATE_WAIT_HEADER
            
            if byte_in == self.PACKET_FOOTER:
                # 收到了正确的包尾，数据包完整，返回 True
                return True
            else:
                # 收到了错误的包尾，数据包无效
                return False
        
        return False # 理论上不会执行到这里，作为保险

    def uart_write(self, byte_value):
        """
        将单个字节包装成 FE-data-FD 的格式并通过串口发送出去。
        :param byte_value: 一个 0-255 之间的整数
        :return: bool - 发送成功返回 True，否则返回 False
        """
        # 1. 检查输入值是否有效
        if not isinstance(byte_value, int) or not 0 <= byte_value <= 255:
            print(f"错误：输入值 '{byte_value}' 无效，请输入一个 0-255 之间的整数。")
            return False

        # 2. 检查串口是否已打开
        if not self.serial or not self.serial.is_open:
            print("错误：串口未打开，无法发送数据。")
            return False
            
        try:
            # 3. 构建并发送数据包
            packet_to_send = bytes([self.PACKET_HEADER, byte_value, self.PACKET_FOOTER])
            self.serial.write(packet_to_send)
            
            print(f"-> 已发送数据包: 0x{packet_to_send[0]:02x} 0x{packet_to_send[1]:02x} 0x{packet_to_send[2]:02x}")
            return True
        except serial.SerialException as e:
            print(f"发送数据时发生错误: {e}")
            return False

    def close(self):
        """
        关闭串口连接。
        """
        if self.serial and self.serial.is_open:
            self.serial.close()
            print(f"串口 {self.port} 已关闭。")
