import time

log_file_path = None
index = 0

# 找到日志文件
while True:
    log_file_path = "/sd/log/log" + str(index) + ".txt"
    try:
        with open(log_file_path) as file:
            index += 1
    except:
        break

def write_log(log_message:str):
    # 记录当前时间，并格式化日志内容
    log_time = str(time.ticks_ms())
    log_entry = log_time + ' ' + log_message
    # 写入日志
    print(log_entry)
    with open(log_file_path, "a") as log_file:
        log_file.write(log_entry + "\n")
