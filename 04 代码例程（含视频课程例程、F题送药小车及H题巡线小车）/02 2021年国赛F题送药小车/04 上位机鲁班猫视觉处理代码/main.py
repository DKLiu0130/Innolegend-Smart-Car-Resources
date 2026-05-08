import os  # [新增] 引入系统操作模块
from uart import PacketParser
from ocr import extract_individual_chars_from_ocr, extract_text_with_ocr, find_and_sort_closest_digits
import cv2
from config import load_config
from time import sleep

config = load_config()

VIDEO_DEV = config.get('Camera', 'dev')
SERIAL_PORT = config.get('Serial', 'port')
BAUD_RATE = config.getint('Serial', 'baudrate')

target = None
cap = cv2.VideoCapture(VIDEO_DEV)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
ser = PacketParser(SERIAL_PORT, BAUD_RATE)

if not cap.isOpened():
    print("错误：无法打开摄像头。")
    exit()

# [新增] 基础图片保存路径
BASE_IMG_DIR = "./img"

# [新增] 自动获取下一个可用的文件夹名称 (例如: ./img/task_1, ./img/task_2...)
def create_new_task_folder(base_dir):
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"创建根目录: {base_dir}")

    # 获取当前目录下所有的文件夹
    existing_folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    
    max_index = 0
    for folder in existing_folders:
        # 假设文件夹命名格式为 "task_数字"
        if folder.startswith("task_"):
            try:
                # 提取数字部分并比较
                idx = int(folder.split("_")[1])
                if idx > max_index:
                    max_index = idx
            except ValueError:
                continue
    
    # 创建新的文件夹，编号 +1
    new_folder_name = f"task_{max_index + 1}"
    new_folder_path = os.path.join(base_dir, new_folder_name)
    os.makedirs(new_folder_path)
    print(f"=== 创建新批次文件夹: {new_folder_path} ===")
    return new_folder_path

if __name__ == "__main__":
    index = 0
    
    # [新增] 用于记录当前的保存路径
    current_save_dir = None
    # [新增] 用于记录上一次的data状态，防止0x1连续发送时重复创建文件夹
    last_data = None 

    while True:
        if ser.uart_read():
            data = ser.data
            cap.read()
            cap.read()
            cap.read()

            

            if data == 0x1 or current_save_dir is None:
                print("检测到开始信号(0x01)或初始化，准备启动...")
                
                # 1. 在这里等待 3 秒
                if data == 0x1: # 只有明确收到0x1才延时，刚启动(None)时通常不需要死等
                    sleep(3) 
                    print("延时结束，清空积压的图像缓存...")

                    # 2. 【关键步骤】清空摄像头缓冲区
                    # 因为睡了3秒，缓冲区里的图是旧的，必须读掉扔弃
                    for _ in range(5): 
                        cap.read()
                    
                # 3. 创建新文件夹
                current_save_dir = create_new_task_folder(BASE_IMG_DIR)
                index = 0
            
            ret, frame = cap.read()

            # -------------------------------

            ocr_results = extract_text_with_ocr(frame)
            char_results = extract_individual_chars_from_ocr(ocr_results)

            # [修改] 使用 os.path.join 拼接路径，保存到动态创建的文件夹中
            if current_save_dir:
                save_path = os.path.join(current_save_dir, f"img_{index}.png")
                cv2.imwrite(save_path, frame)
            else:
                # 理论上不会走到这里，但为了保险
                cv2.imwrite("./img/fallback_" + str(index) + '.png', frame)

            print("data is " + str(data))

            index += 1
            
            if len(char_results) == 0:
                print("未检测到字符。")
                continue
            print(f'字符队列{char_results}')

            
            if data == 0x1:
                char_results = find_and_sort_closest_digits(char_results, 1, frame.shape)
                # ... (以下逻辑保持不变) ...
                target = char_results[0][1]
                if target == '1':
                    ser.uart_write(0x2)
                elif target == '2':
                    ser.uart_write(0x4)
                else:
                    ser.uart_write(0x1)
                    
                print(f'目标变为 {target}')

            elif data == 0x2:
                # ... (以下逻辑保持不变) ...
                char_results = find_and_sort_closest_digits(char_results, 2, frame.shape)
                char_results = [char_result[1] for char_result in char_results]
                print(f'路口2检测结果:{char_results}')

                if target in char_results:
                    if target == char_results[0]:
                        ser.uart_write(0x2)
                    else:
                        ser.uart_write(0x4)
                else:
                    ser.uart_write(0x1)

            elif data == 0x4:
                # ... (以下逻辑保持不变) ...
                char_results = find_and_sort_closest_digits(char_results, 4, frame.shape)
                char_results = [char_result[1] for char_result in char_results]
                print(f'路口3检测结果:{char_results}')

                if target in char_results:
                    if target in char_results[0 : 2]:
                        ser.uart_write(0x2)
                    else:
                        ser.uart_write(0x4)
                else:
                    ser.uart_write(0x2)
            
            elif data == 0x8:
                # ... (以下逻辑保持不变) ...
                char_results = find_and_sort_closest_digits(char_results, 2, frame.shape)
                char_results = [char_result[1] for char_result in char_results]
                print(f'路口4检测结果:{char_results}')

                if target in char_results:
                    if target == char_results[0]:
                        ser.uart_write(0x2)
                    else:
                        ser.uart_write(0x4)
                else:
                    ser.uart_write(0x2)