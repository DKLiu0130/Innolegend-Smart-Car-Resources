import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ocr_engine = RapidOCR()

def extract_text_with_ocr(image):
    """
    使用 RapidOCR 提取画面中所有的文字。
    
    :param image: 输入的图像 (OpenCV BGR 格式)。
    :return: 一个包含所有识别结果的列表。
             格式为: [ [[x, y, w, h], text, confidence], ... ]
    """
    # RapidOCR 需要 BGR 格式的图像，这与 cv2.imread 读入的格式一致
    result, _ = ocr_engine(image)
    
    output = []
    if result:
        for box, text, confidence in result:
            # box 是四个点的坐标 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            # 我们需要将其转换为 [x, y, w, h] 格式
            points = np.array(box, dtype=np.int32)
            x, y, w, h = cv2.boundingRect(points)
            
            output.append([[x, y, w, h], text, confidence])
            
    return output

def extract_individual_chars_from_ocr(ocr_results):
    """
    对 RapidOCR 的结果进行后处理，将识别出的单词拆分为单个字符及其估算边界框。
    注意：此方法假设字符是等宽且水平排列的，对于倾斜或艺术字体可能不准确。

    :param ocr_results: extract_text_with_ocr 函数的输出。
    :return: 格式与输入类似，但每个元素代表一个字符。
             格式为: [ [[x, y, w, h], char, confidence], ... ]
    """
    char_results = []
    for box, text, confidence in ocr_results:
        x, y, w, h = box
        # 如果文本为空或长度为0，则跳过
        if not text:
            continue
        
        # 估算每个字符的平均宽度
        char_width = w / len(text)
        
        current_x = x
        for char in text:
            # 创建每个字符的估算边界框
            # 将坐标和尺寸转换为整数
            char_box = [int(current_x), y, int(char_width), h]
            char_results.append([char_box, char, confidence])
            # 更新下一个字符的起始 x 坐标
            current_x += char_width
            
    return char_results

def find_and_sort_closest_digits(char_results, x, image_shape):
    """
    从OCR字符结果中筛选出距离图像中心最近的x个数字，
    并沿着图像的长边（例如640x480图像中的640边）从左到右或从上到下进行排序。

    :param char_results: extract_individual_chars_from_ocr 的输出结果。
    :param x: 需要选出的最近数字的数量。
    :param image_shape: 原始图像的形状 (height, width, channels)，用于确定中心点和长边。
    :return: 一个按长边排序后的包含x个（或更少）数字信息的列表。
    """
    # 1. 获取图像中心
    img_height, img_width, _ = image_shape
    img_center_x, img_center_y = img_width / 2, img_height / 2

    # 2. 筛选出所有数字，并计算它们到图像中心的距离
    digits_with_dist = []
    for result in char_results:
        box, char, confidence = result
        if char.isdigit():
            x_coord, y_coord, w, h = box
            # 计算数字中心点
            char_center_x = x_coord + w / 2
            char_center_y = y_coord + h / 2
            # 计算欧氏距离的平方（避免开方，效果相同）
            distance_sq = (char_center_x - img_center_x)**2 + (char_center_y - img_center_y)**2
            digits_with_dist.append({'data': result, 'distance': distance_sq})

    # 3. 按距离从小到大排序
    digits_with_dist.sort(key=lambda item: item['distance'])

    # 4. 选出最近的 x 个数字（如果总数不足x，则全选）
    num_to_select = min(x, len(digits_with_dist))
    closest_digits_data = [item['data'] for item in digits_with_dist[:num_to_select]]

    # 5. 确定长边并进行排序
    # 如果宽度大于或等于高度，长边是X轴
    if img_width >= img_height:
        # 按 x 坐标排序（从左到右）
        closest_digits_data.sort(key=lambda item: item[0][0])
    else: # 否则长边是Y轴
        # 按 y 坐标排序（从上到下）
        closest_digits_data.sort(key=lambda item: item[0][1])
        
    return closest_digits_data


# --- 主程序：演示如何使用以上函数 ---
if __name__ == '__main__':
    # 注意：运行此示例需要安装:
    # pip install opencv-python numpy rapidocr-onnxruntime

    # --- 使用您的图像进行分割处理 ---
    image_filename = "2025-08-31-160002.jpg"
    output_filename = "annotated_digits_output.jpg"

    # 1. 读取图像
    image = cv2.imread(image_filename)
    print(image.size())
    if image is None:
        print(f"错误：无法读取图像 '{image_filename}'。请确保文件存在于脚本所在的目录。")
    else:
        print(f"成功读取图像: '{image_filename}'")
        
        # 创建一个用于绘制的图像副本
        annotated_image = image.copy()

        # 2. 提取整段文本
        ocr_results = extract_text_with_ocr(image)
        print("\n--- 原始OCR识别结果 ---")
        print(ocr_results)

        # 3. 将文本分割为单个字符
        char_results = extract_individual_chars_from_ocr(ocr_results)
        print("\n--- 单个字符分割结果 ---")

        # 4. 遍历分割后的结果并在图像上绘制每个数字的范围
        for box, char, conf in char_results:
            # 我们只对数字感兴趣
            if char.isdigit():
                x, y, w, h = box
                print(f"- 找到数字: '{char}', 位置: [x={x}, y={y}, w={w}, h={h}]")
                
                # 绘制矩形框 (绿色)
                cv2.rectangle(annotated_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # 在框上方标注数字 (红色)
                label = f"{char}"
                cv2.putText(annotated_image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        # 5. 显示结果图像
        cv2.imshow("Annotated Digits", annotated_image)
        print(f"\n已显示标注所有数字后的图像。按任意键将会保存图像并退出。")
        cv2.waitKey(0)

        # 6. 保存图像
        cv2.imwrite(output_filename, annotated_image)
        print(f"图像已成功保存为 '{output_filename}'")

        # 7. 关闭所有窗口
        cv2.destroyAllWindows()


