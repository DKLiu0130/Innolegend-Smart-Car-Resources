from logger import write_log
import time
import os

def dir_exists(path):
    """
    检查目录是否存在
    """
    try:
        os.listdir(path)
        return True
    except:
        return False

def detect_and_sort_numbers(k, x, sensor, model, debug = True):
    """
    连续拍摄k帧，检测数字，提取出现次数前x多的数字，按平均中心点x坐标排序
    
    :param k: 拍摄帧数
    :param x: 提取前x个数字
    :param sensor: 传感器对象
    :param model: 模型对象
    :param debug: 调试模式，True时保存第一帧图像
    :return: 按x坐标排序的数字数组，不足x个用0补充
    """
    try:
        write_log("开始连续拍摄 " + str(k) + " 帧进行检测")
        
        # 如果是debug模式，初始化保存目录
        if debug:
            save_dir = "/sd/shot"
            try:
                # 检查目录是否存在，不存在则创建
                if not dir_exists(save_dir):
                    os.makedirs(save_dir)
                    write_log("创建debug图像保存目录: " + save_dir)
            except Exception as e:
                write_log("创建debug目录失败: " + str(e))
                debug = False  # 创建失败则禁用debug模式
        
        # 存储每个数字的信息：{数字: [出现次数, x坐标总和]}
        number_stats = {}
        
        # 连续拍摄k帧
        for frame_idx in range(k):
            img = sensor.snapshot()
            
            # debug模式下保存第一帧图像
            if debug and frame_idx == 0:
                try:
                    # 生成时间戳文件名
                    timestamp = time.ticks_ms()
                    filename = "frame_" + str(timestamp) + ".jpg"
                    filepath = save_dir + "/" + filename
                    
                    # 保存图像
                    img.save(filepath)
                    write_log("DEBUG: 保存第一帧图像到 " + filepath)
                except Exception as e:
                    write_log("DEBUG: 保存第一帧图像失败: " + str(e))
        
        # 连续拍摄k帧
        for frame_idx in range(k):
            img = sensor.snapshot()
            
            # 进行检测
            results = model.detect(img)
            
            if results:
                write_log("第 " + str(frame_idx + 1) + " 帧检测到 " + str(len(results)) + " 个数字")
                
                # 处理检测结果
                for result in results:
                    bbox, label_id, confidence = result[0], result[1], result[2]
                    x_coord, y_coord, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
                    
                    # 计算中心点x坐标
                    center_x = x_coord + w // 2
                    
                    # 更新统计信息
                    if label_id not in number_stats:
                        number_stats[label_id] = [0, 0]  # [出现次数, x坐标总和]
                    
                    number_stats[label_id][0] += 1  # 增加出现次数
                    number_stats[label_id][1] += center_x  # 累加x坐标
                    
            else:
                write_log("第 " + str(frame_idx + 1) + " 帧未检测到数字")


        write_log("拍摄完成，开始分析结果...")

        # 如果没有检测到任何数字
        if not number_stats:
            write_log("未检测到任何数字，返回全0数组")
            return [0] * x

        
        # 计算每个数字的平均中心点x坐标
        number_avg_x = {}
        for number, stats in number_stats.items():
            count, x_sum = stats[0], stats[1]
            avg_x = x_sum // count  # 整数除法计算平均值
            number_avg_x[number] = (count, avg_x)
            write_log("数字 " + str(number) + ": 出现 " + str(count) + " 次, 平均x=" + str(avg_x))

        # 按出现次数排序，取前x个
        sorted_by_count = sorted(number_avg_x.items(), key=lambda item: item[1][0], reverse=True)
        top_x_numbers = sorted_by_count[:x]

        write_log("前 " + str(min(x, len(sorted_by_count))) + " 个出现次数最多的数字:")
        for number, (count, avg_x) in top_x_numbers:
            write_log("  数字 " + str(number) + ": " + str(count) + " 次, 平均x=" + str(avg_x))

        # 按平均x坐标从左到右排序
        sorted_by_x = sorted(top_x_numbers, key=lambda item: item[1][1])  # 按avg_x排序
        
        # 提取数字并补充0
        result_array = []
        for number, (count, avg_x) in sorted_by_x:
            result_array.append(number)
        
        # 用0补充到x个数字
        while len(result_array) < x:
            result_array.append(0)
        
        # 只取前x个
        result_array = result_array[:x]
        
        write_log("检测结果: " + str(result_array))
        
        return result_array
        
    except Exception as e:
        write_log("检测和排序过程发生错误: " + str(e))
        return [0] * x