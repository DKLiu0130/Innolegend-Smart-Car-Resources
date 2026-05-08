import time
import os

log_file_path = None
index = 0

# 找到日志文件
while True:
    log_file_path = "log/log" + str(index) + ".txt"
    try:
        with open(log_file_path) as file:
            index += 1
    except:
        break

def write_log(log_message: str):
    """
    记录日志信息到文件和串口
    
    :param log_message: 日志消息
    """
    # 记录当前时间，并格式化日志内容
    log_time = str(int(time.time() * 1000))
    log_entry = log_time + ' ' + log_message
    
    # 写入串口（调试输出）
    print(log_entry)
    
    # 写入日志文件
    try:
        with open(log_file_path, "a") as log_file:
            log_file.write(log_entry + "\n")
    except Exception as e:
        print("写入日志文件失败: " + str(e))
