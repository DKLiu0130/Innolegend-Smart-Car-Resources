# 导入 PacketParser 类
# 注意：你需要确保 serial_parser.py 和这个新文件在同一个目录下
try:
    from uart import PacketParser
except ImportError:
    print("错误: 无法找到 'serial_parser.py'。")
    print("请确保 'serial_parser.py' 文件与此脚本位于同一目录中。")
    exit()

import serial

from config import load_config
config = load_config()

# --- 配置 ---
# 在PC上测试时，请将 SERIAL_PORT 修改为 PC 对应的串口号
# 例如: PC_SERIAL_PORT = 'COM3' 或 '/dev/ttyUSB0'
PC_SERIAL_PORT = config.get('Serial', 'port') # <--- 请根据您的PC修改这里
BAUD_RATE = config.getint('Serial', 'baudrate')


def main():
    """主函数，运行交互式串口发送程序"""
    
    # 定义输入到发送字节的映射关系
    command_map = {
        '1': 0x01,
        '2': 0x02,
        '3': 0x04,
        '4': 0x08,
    }
    
    parser = None
    try:
        # 初始化 PacketParser，它会自动打开串口
        parser = PacketParser(PC_SERIAL_PORT, BAUD_RATE)
        
        print("\n--- 串口指令发送程序 ---")
        print("请输入数字 1, 2, 3, 或 4 来发送对应的指令。")
        print("  - 输入 '1' 发送 0x01")
        print("  - 输入 '2' 发送 0x02")
        print("  - 输入 '3' 发送 0x04")
        print("  - 输入 '4' 发送 0x08")
        print("输入 'q' 或 'exit' 退出程序。")
        print("-" * 28)

        while True:
            # 获取用户输入
            user_input = input("请输入指令 > ").strip()

            # 检查是否退出
            if user_input.lower() in ['q', 'exit']:
                print("正在退出...")
                break
            
            # 检查输入是否有效
            if user_input in command_map:
                byte_to_send = command_map[user_input]
                print(f"准备发送指令 '{user_input}' -> 0x{byte_to_send:02x}")
                # 调用 uart_write 发送数据
                parser.uart_write(byte_to_send)
            else:
                print(f"无效输入: '{user_input}'。请输入 1, 2, 3, 4 中的一个。")
            
            print() # 增加空行，使输出更清晰

    except serial.SerialException:
        print(f"错误：无法启动解析器，请检查串口 '{PC_SERIAL_PORT}' 是否正确并且未被占用。")
    except KeyboardInterrupt:
        print("\n程序被用户中断。")
    finally:
        # 确保在程序退出时关闭串口
        if parser:
            parser.close()

if __name__ == "__main__":
    main()
