from logger import write_log
import time
import os
import image
import math


def dir_exists(path):
    """
    检查目录是否存在
    """
    try:
        os.listdir(path)
        return True
    except:
        return False


# ---------------- FOMO 回调后处理 ----------------
# 置信度阈值（与官方例程一致，FOMO通道将被映射到0-255后阈值判断）
_MIN_CONF = 0.5
_threshold_list = [(math.ceil(_MIN_CONF * 255), 255)]


def _fomo_post_process(model, inputs, outputs):
    # 输出形状: (batch, out_h, out_w, out_c)
    ob, oh, ow, oc = model.output_shape[0]

    # 将输出热力图坐标映射回输入ROI坐标
    x_scale = inputs[0].roi[2] / ow
    y_scale = inputs[0].roi[3] / oh
    scale = min(x_scale, y_scale)

    x_offset = ((inputs[0].roi[2] - (ow * scale)) / 2) + inputs[0].roi[0]
    y_offset = ((inputs[0].roi[3] - (oh * scale)) / 2) + inputs[0].roi[1]

    # 每一类一个列表
    detections_per_class = [[] for _ in range(oc)]

    for c in range(oc):
        # 将该类通道映射为8位图像，方便find_blobs
        cls_img = image.Image(outputs[0][0, :, :, c] * 255)
        blobs = cls_img.find_blobs(
            _threshold_list, x_stride=1, y_stride=1, area_threshold=1, pixels_threshold=1
        )
        for b in blobs:
            x, y, w, h = b.rect()
            # 用该区域的亮度均值做score（0~1）
            score = cls_img.get_statistics(thresholds=_threshold_list, roi=b.rect()).l_mean() / 255.0

            # 映射回输入ROI坐标系
            rx = int((x * scale) + x_offset)
            ry = int((y * scale) + y_offset)
            rw = int(w * scale)
            rh = int(h * scale)

            detections_per_class[c].append((rx, ry, rw, rh, score))

    return detections_per_class


# ---------------- 主流程：多帧统计与排序 ----------------

def detect_and_sort_numbers(k, x, sensor, model, debug=True):
    """
    连续拍摄k帧，检测数字，提取出现次数前x多的数字，按平均中心点x坐标排序

    :param k: 拍摄帧数
    :param x: 提取前x个数字
    :param sensor: 传感器对象
    :param model: 模型对象（FOMO）
    :param debug: 调试模式，True时保存第一帧图像
    :return: 按x坐标排序的数字数组，不足x个用0补充
    """
    try:
        write_log("开始连续拍摄 " + str(k) + " 帧进行检测")

        # 如果是debug模式，初始化保存目录
        if debug:
            save_dir = "shot"
            try:
                # 检查目录是否存在，不存在则创建
                if not dir_exists(save_dir):
                    os.mkdir(save_dir)
                    write_log("创建debug图像保存目录: " + save_dir)
            except Exception as e:
                write_log("创建debug目录失败: " + str(e))
                debug = False  # 创建失败则禁用debug模式

        # 存储每个数字的信息：{数字(类别id): [出现次数, x坐标总和]}
        number_stats = {}

        # 连续拍摄k帧
        for frame_idx in range(k):
            img = sensor.snapshot()

            # debug模式下保存第一帧图像
            if debug and frame_idx == 0:
                try:
                    timestamp = int(time.time() * 1000)
                    filename = "frame_" + str(timestamp) + ".pgm"
                    filepath = save_dir + "/" + filename
                    img.save(filepath)
                    write_log("DEBUG: 保存第一帧图像到 " + filepath)
                except Exception as e:
                    write_log("DEBUG: 保存第一帧图像失败: " + str(e))

            # 使用FOMO回调进行预测
            try:
                detections_per_class = model.predict([img], callback=_fomo_post_process)
            except Exception as e:
                write_log("第 " + str(frame_idx + 1) + " 帧检测失败: " + str(e))
                continue

            frame_detections = 0
            # detections_per_class: index为类别id，0为background
            for class_id, det_list in enumerate(detections_per_class):
                if class_id == 0:
                    continue  # 跳过背景类
                if not det_list:
                    continue

                frame_detections += len(det_list)

                for (rx, ry, rw, rh, score) in det_list:
                    center_x = rx + (rw // 2)

                    # 更新统计信息
                    if class_id not in number_stats:
                        number_stats[class_id] = [0, 0]  # [出现次数, x坐标总和]
                    number_stats[class_id][0] += 1
                    number_stats[class_id][1] += center_x

            if frame_detections > 0:
                write_log("第 " + str(frame_idx + 1) + " 帧检测到 " + str(frame_detections) + " 个数字")
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
        result_array = [num for (num, _) in sorted_by_x]

        # 用0补充到x个
        while len(result_array) < x:
            result_array.append(0)

        # 只取前x个
        result_array = result_array[:x]

        write_log("检测结果: " + str(result_array))
        return result_array

    except Exception as e:
        write_log("检测和排序过程发生错误: " + str(e))
        return [0] * x
