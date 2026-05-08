import sensor
import image
import time
import os
import utime
from fpioa_manager import fm
from Maix import GPIO
from logger import write_log

class Camera:
    """
    K210摄像头控制类
    用于拍摄224x224分辨率的图像并保存到SD卡
    """

    def __init__(self):
        """
        初始化摄像头
        """
        self.img_count = 0
        self.save_path = "/sd/img"
        self.current_img = None  # 存储当前拍摄的图像
        self.save_flag = False   # 保存标志位
        self.init_camera()
        self.init_storage()

    def init_camera(self):
        """
        初始化摄像头传感器
        """
        try:
            # 复位和初始化摄像头，执行sensor.run(0)停止
            sensor.reset()

            # 设置水平镜像
            sensor.set_hmirror(1)

            # 设置垂直翻转
            sensor.set_vflip(1)

            # 设置像素格式为彩色 RGB565
            sensor.set_pixformat(sensor.RGB565)

            # 设置帧大小为 QVGA (320x240)
            sensor.set_framesize(sensor.QVGA)

            # 设置窗口
            sensor.set_windowing((0, 0, 224, 224))

            # 等待设置生效
            sensor.skip_frames(time=2000)

            # 启动摄像头
            sensor.run(1)

            write_log("摄像头初始化成功")
            print("摄像头初始化成功")

        except Exception as e:
            write_log("摄像头初始化失败: " + str(e))
            print("摄像头初始化失败: " + str(e))
            raise e

    def init_storage(self):
        """
        初始化存储目录
        """
        try:
            # 检查SD卡是否挂载
            if "sd" not in os.listdir("/"):
                write_log("SD卡未挂载")
                print("SD卡未挂载")
                return False

            # 创建图像保存目录
            if not self.dir_exists(self.save_path):
                os.makedirs(self.save_path)
                write_log("创建目录: " + self.save_path)
                print("创建目录: " + self.save_path)

            # 获取现有图像数量
            self.img_count = self.get_existing_image_count()
            write_log("存储初始化成功，已有图像: " + str(self.img_count) + " 张")
            print("存储初始化成功，已有图像: " + str(self.img_count) + " 张")
            return True

        except Exception as e:
            write_log("存储初始化失败: " + str(e))
            print("存储初始化失败: " + str(e))
            return False

    def dir_exists(self, path):
        """
        检查目录是否存在
        """
        try:
            os.listdir(path)
            return True
        except:
            return False

    def get_existing_image_count(self):
        """
        获取已存在的图像数量
        """
        try:
            files = os.listdir(self.save_path)
            jpg_files = [f for f in files if f.endswith('.jpg')]
            return len(jpg_files)
        except:
            return 0

    def continuous_capture(self):
        """
        持续拍摄模式，不停地拍摄图像但不保存
        只有当save_flag为True时才保存图像
        """
        try:
            # 持续拍摄图像
            self.current_img = sensor.snapshot()
            
            # 检查是否需要保存
            if self.save_flag:
                self.save_current_image()
                self.save_flag = False  # 重置保存标志
                
        except Exception as e:
            print("持续拍摄失败: " + str(e))
    
    def save_current_image(self, filename=None):
        """
        保存当前拍摄的图像
        
        :param filename: 指定文件名，如果为None则自动生成
        :return: 保存的文件路径，失败返回None
        """
        if self.current_img is None:
            print("没有可保存的图像")
            return None
            
        try:
            # 生成文件名
            if filename is None:
                self.img_count += 1
                # 手动实现6位数字填充
                num_str = str(self.img_count)
                while len(num_str) < 6:
                    num_str = "0" + num_str
                filename = "img_" + num_str + ".jpg"

            # 确保文件名以.jpg结尾
            if not filename.endswith('.jpg'):
                filename += '.jpg'

            # 完整文件路径
            filepath = self.save_path + "/" + filename

            # 保存图像
            self.current_img.save(filepath)

            write_log("图像保存成功: " + filepath)
            print("图像保存成功: " + filepath)

            return filepath

        except Exception as e:
            write_log("图像保存失败: " + str(e))
            print("图像保存失败: " + str(e))
            return None
    
    def trigger_save(self):
        """
        触发保存当前图像
        """
        self.save_flag = True

    def capture_multiple(self, count=1, interval_ms=1000):
        """
        连续拍摄多张图像

        :param count: 拍摄数量
        :param interval_ms: 拍摄间隔(毫秒)
        :return: 成功拍摄的图像路径列表
        """
        captured_files = []

        write_log("开始连续拍摄 " + str(count) + " 张图像")
        print("开始连续拍摄 " + str(count) + " 张图像")

        for i in range(count):
            self.continuous_capture()
            if self.save_flag:
                self.save_current_image()
                self.save_flag = False
                captured_files.append("saved")
                print("完成 " + str(i+1) + "/" + str(count))

            # 最后一张不需要等待
            if i < count - 1:
                time.sleep_ms(interval_ms)

        write_log("连续拍摄完成，成功: " + str(len(captured_files)) + "/" + str(count))
        print("连续拍摄完成，成功: " + str(len(captured_files)) + "/" + str(count))

        return captured_files

    def preview_mode(self, duration_sec=10):
        """
        预览模式，显示摄像头画面

        :param duration_sec: 预览时长(秒)
        """
        print("进入预览模式 " + str(duration_sec) + " 秒")
        start_time = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < duration_sec * 1000:
            img = sensor.snapshot()
            # 在这里可以添加LCD显示代码
            time.sleep_ms(50)  # 20fps

        print("预览模式结束")

    def get_camera_info(self):
        """
        获取摄像头信息
        """
        try:
            info = {
                "pixel_format": "RGB565",
                "frame_size": "QVGA -> 224x224",
                "save_path": self.save_path,
                "image_count": self.img_count
            }
            return info
        except Exception as e:
            print("获取摄像头信息失败: " + str(e))
            return None

# 创建全局摄像头实例
camera = Camera()

# 按键配置和中断设置
boot_key = 16

fm.register(boot_key, fm.fpioa.GPIOHS0)

# 构建按键对象
KEY = GPIO(GPIO.GPIOHS0, GPIO.IN, GPIO.PULL_UP)

# 按键中断函数 - 触发保存照片
def key_callback(KEY):
    """
    按键中断回调函数 - 触发保存当前图像
    """
    utime.sleep_ms(10)  # 消除抖动
    if KEY.value() == 0:  # 确认按键被按下
        print("按键触发，保存当前图像...")
        camera.trigger_save()

# 开启中断，下降沿触发
KEY.irq(key_callback, GPIO.IRQ_FALLING)

# 便捷函数
def take_photo(filename=None):
    """
    快速拍照函数
    """
    return camera.save_current_image(filename)

def trigger_save():
    """
    触发保存当前图像
    """
    camera.trigger_save()

def take_photos(count=1, interval_ms=1000):
    """
    快速连拍函数
    """
    return camera.capture_multiple(count, interval_ms)

def preview(duration_sec=10):
    """
    快速预览函数
    """
    camera.preview_mode(duration_sec)

def camera_info():
    """
    获取摄像头信息
    """
    return camera.get_camera_info()

if __name__ == "__main__":
    print("摄像头持续拍摄模式启动")
    print("按下按键保存当前图像...")
    
    while True:
        # 持续拍摄，不停更新current_img
        camera.continuous_capture()
        # 短暂延时，避免CPU占用过高
        time.sleep_ms(50)  # 20fps

