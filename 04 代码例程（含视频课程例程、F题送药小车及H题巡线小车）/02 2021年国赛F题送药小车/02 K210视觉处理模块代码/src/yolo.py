import sensor
import image
import time
import KPU as kpu
import gc
from logger import write_log

class YOLO:
    """
    K210 YOLO检测器类
    用于加载模型并进行数字识别
    """
    
    def __init__(self, model_path="/sd/model-234356.kmodel", 
                 labels=['4', '6', '7', '8', '1', '3', '5', '2'],
                 anchors= [0.81, 1.03, 1.34, 1.59, 2.28, 2.94, 1.75, 2.0, 1.09, 1.28],
                 input_size=(224, 224),
                 threshold=0.5,
                 nms_threshold=0.2):
        """
        初始化YOLO检测器
        
        :param model_path: 模型文件路径
        :param labels: 标签列表，用于ID映射
        :param anchors: anchor参数
        :param input_size: 输入图像尺寸
        :param threshold: 检测阈值
        :param nms_threshold: NMS阈值
        """
        self.model_path = model_path
        self.labels = labels
        self.anchors = anchors
        self.input_size = input_size
        self.threshold = threshold
        self.nms_threshold = nms_threshold
        self.task = None
        
        # 初始化模型
        self.init_model()
    
    def init_model(self):
        """
        初始化KPU模型
        """
        try:
            write_log("开始加载YOLO模型: " + self.model_path)
            print("开始加载YOLO模型: " + self.model_path)
            
            # 加载模型
            self.task = kpu.load(self.model_path)
            
            # 初始化YOLO2
            kpu.init_yolo2(self.task, self.threshold, self.nms_threshold, 5, self.anchors)
            
            write_log("YOLO模型加载成功")
            print("YOLO模型加载成功")
            
        except Exception as e:
            write_log("YOLO模型加载失败: " + str(e))
            print("YOLO模型加载失败: " + str(e))
            raise e
    
    def preprocess_image(self, img):
        """
        预处理图像：缩放到224x224并转换为AI格式
        
        :param img: 输入图像
        :return: 处理后的图像
        """
        try:
            # 检查输入图像是否有效
            if img is None:
                print("输入图像为空")
                return None
            
            # 缩放图像到224x224
            if img.width() != self.input_size[0] or img.height() != self.input_size[1]:
                img_resized = img.resize(self.input_size[0], self.input_size[1])
            else:
                img_resized = img
            
            # 将RGB565转换为RGB888（AI格式）
            # 这是K210硬件特性要求的关键步骤
            img_resized.pix_to_ai()
            
            return img_resized
            
        except Exception as e:
            print("图像预处理失败: " + str(e))
            return None
    
    def detect(self, img):
        """
        检测图像中的数字
        
        :param img: 输入图像
        :return: 检测结果列表，格式为 [[x,y,w,h], id, conf]
        """
        if self.task is None:
            print("模型未初始化")
            return []
        
        try:
            # 预处理图像
            processed_img = self.preprocess_image(img)
            if processed_img is None:
                return []
            
            # 运行推理
            start_time = time.ticks_ms()
            objects = kpu.run_yolo2(self.task, processed_img)
            inference_time = time.ticks_diff(time.ticks_ms(), start_time)
            
            print("推理耗时: " + str(inference_time) + "ms")
            
            # 解析结果
            results = []
            if objects:
                for obj in objects:
                    # 获取边界框坐标
                    rect = obj.rect()  # (x, y, w, h)
                    x, y, w, h = rect[0], rect[1], rect[2], rect[3]
                    
                    # 获取类别ID和置信度
                    class_id = obj.classid()
                    confidence = obj.value()
                    
                    # 映射到实际标签
                    if 0 <= class_id < len(self.labels):
                        label_id = int(self.labels[class_id])  # 转换为数字ID
                    else:
                        label_id = class_id  # 如果映射失败，使用原始ID
                    
                    # 构建结果格式: [[x,y,w,h], id, conf]
                    result = [[x, y, w, h], label_id, confidence]
                    results.append(result)
                    
                    print("检测到: ID=" + str(label_id) + 
                          ", 位置=(" + str(x) + "," + str(y) + "," + str(w) + "," + str(h) + ")" +
                          ", 置信度=" + str(confidence))
            
            return results
            
        except Exception as e:
            print("检测失败: " + str(e))
            return []
    
    def detect_raw(self, img):
        """
        检测图像并返回原始KPU结果格式
        
        :param img: 输入图像
        :return: 原始检测结果，格式类似 [{"x":78, "y":151, "w":56, "h":49, "value":0.681252, "classid":4, "index":0, "objnum":1}]
        """
        if self.task is None:
            print("模型未初始化")
            return []
        
        try:
            # 预处理图像
            processed_img = self.preprocess_image(img)
            if processed_img is None:
                return []
            
            # 运行推理
            objects = kpu.run_yolo2(self.task, processed_img)
            
            # 转换为字典格式
            results = []
            if objects:
                for i, obj in enumerate(objects):
                    rect = obj.rect()
                    result_dict = {
                        "x": rect[0],
                        "y": rect[1], 
                        "w": rect[2],
                        "h": rect[3],
                        "value": obj.value(),
                        "classid": obj.classid(),
                        "index": i,
                        "objnum": len(objects)
                    }
                    results.append(result_dict)
            
            return results
            
        except Exception as e:
            print("原始检测失败: " + str(e))
            return []
    
    def draw_results(self, img, results):
        """
        在图像上绘制检测结果
        
        :param img: 图像对象
        :param results: 检测结果列表
        :return: 绘制后的图像
        """
        try:
            for result in results:
                if len(result) >= 3:
                    # 解析结果
                    bbox, label_id, confidence = result[0], result[1], result[2]
                    x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
                    
                    # 绘制边界框
                    img.draw_rectangle(x, y, w, h, color=(255, 0, 0), thickness=2)
                    
                    # 绘制标签和置信度
                    text = str(label_id) + ":" + str(round(confidence, 2))
                    img.draw_string(x, y-15, text, color=(255, 0, 0), scale=2)
            
            return img
            
        except Exception as e:
            print("绘制结果失败: " + str(e))
            return img
    
    def cleanup(self):
        """
        清理资源
        """
        try:
            if self.task is not None:
                kpu.deinit(self.task)
                self.task = None
                write_log("YOLO模型资源已清理")
                print("YOLO模型资源已清理")
        except Exception as e:
            print("清理资源失败: " + str(e))
        
        # 垃圾回收
        gc.collect()
    
    def __del__(self):
        """
        析构函数，自动清理资源
        """
        self.cleanup()

