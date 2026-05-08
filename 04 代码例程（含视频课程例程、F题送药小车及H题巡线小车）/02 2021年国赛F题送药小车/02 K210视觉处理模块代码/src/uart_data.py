# 阻塞式数据包解析器类
class PacketParser:
    """
    一个用于阻塞式解析特定格式串行数据包的类。
    数据包格式: 0xFE (头) + 1字节数据 + 0xFD (尾)
    """
    # 定义状态常量
    STATE_WAIT_HEADER = 0
    STATE_WAIT_DATA = 1
    STATE_WAIT_FOOTER = 2

    # 定义协议字节
    PACKET_HEADER = 0xFE
    PACKET_FOOTER = 0xFD

    def __init__(self, uart_instance):
        """
        初始化解析器
        :param uart_instance: UART实例 (例如: uart1 或 uart2)
        """
        self.uart = uart_instance
        
        # 内部状态和数据
        self.state = self.STATE_WAIT_HEADER
        self.data = None

    def uart_read(self):
        """
        阻塞式地从串口读取一个字节，并根据状态机进行处理。
        该方法每次被调用，都会阻塞直到接收到一个字节。

        - 第一次调用（等待包头）: 返回 False
        - 第二次调用（等待数据）: 返回 False  
        - 第三次调用（等待包尾）: 如果包尾正确，返回 True；否则返回 False
        
        :return: bool - 仅在第三次调用且包尾正确时返回 True。
        """
        # 阻塞等待接收一个字节
        while not self.uart.any():
            pass  # 等待数据到达
        
        # 读取一个字节
        byte_data = self.uart.read(1)
        if not byte_data:
            return False
        
        byte_in = byte_data[0]
        
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
        
        return False  # 理论上不会执行到这里，作为保险

    def uart_write(self, data: int):
        """
        发送单个字节数据，按照协议格式打包
        数据包格式: 0xFE (头) + 1字节数据 + 0xFD (尾)
        
        :param data: 要发送的字节数据 (0-255)
        """
        # 构建数据包
        packet = bytearray([
            self.PACKET_HEADER,  # 帧头 0xFE
            data,                # 数据字节
            self.PACKET_FOOTER   # 帧尾 0xFD
        ])
        
        # 通过串口发送数据包
        self.uart.write(packet)
