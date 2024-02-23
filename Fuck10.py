import cv2
import pytesseract
import numpy as np
import DataStruct as DS
from ppadb.client import Client as AdbClient
from skimage.metrics import structural_similarity as ssim

kGameCol = 10
kGameRow = 16
kGameSum = 10
kGameImageName = 'game.jpg'

# ADB 链接手机
# 创建ADB客户端对象

client = AdbClient(host="127.0.0.1", port=5037)

# 获取已连接的设备列表
devices = client.devices()
if len(devices) == 0:
    print("未检测到手机设备连接")
    exit(0)

# 默认取第一个
device = devices[0]

# 获取屏幕截图
screenshot = device.screencap()

# 将屏幕截图转换为OpenCV图像
screen_shot_image = cv2.imdecode(np.frombuffer(screenshot, np.uint8), cv2.IMREAD_COLOR)
# cv2.imwrite(kGameImageName, screen_shot_image)

def rect_sort(ocr_result):
    # 返回用于排序的值
    return ocr_result.rect.y * 10 + ocr_result.rect.x


def get_ocr_result(image):
    # 将图像转换为灰度图
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 全局阈值法二值化
    threshold_value = 10  # 阈值
    max_value = 255  # 最大像素值
    ret, gray = cv2.threshold(gray, threshold_value, max_value, cv2.THRESH_BINARY)

    # 使用阈值化将非白色像素设为前景，白色像素设为背景
    _, thresholded = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # 查找非白色像素区域的轮廓
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 获取非白色像素区域的包围盒
    bounding_boxes = [cv2.boundingRect(contour) for contour in contours]

    ocr_result = []
    # 对每个包围盒进行裁剪
    for bbox in bounding_boxes:
        bx, by, bw, bh = bbox
        ew = 12
        eh = 12
        bx -= ew
        by -= eh
        bw += ew * 2
        bh += eh * 2

        digit_image = image[by:by + bh, bx:bx + bw]
        # 比较图片相似度
        max_siml = -1
        max_k = -1
        gray_height, gray_width, gray_channel = digit_image.shape
        gray_digit_img = cv2.cvtColor(digit_image, cv2.COLOR_BGR2GRAY)
        for k in range(1, 10):
            img = cv2.imread("std_img/" + str(k) + ".png")
            gray_img = cv2.cvtColor(cv2.resize(img, (gray_width, gray_height)), cv2.COLOR_BGR2GRAY)
            # 计算SSIM
            similarity = ssim(gray_digit_img, gray_img)
            # print("Similarity:", similarity)
            if similarity > 0.7 and similarity > max_siml:
                max_siml = similarity
                max_k = k
        # print("max Similarity: ", max_siml, " digit: ", max_k)
        if max_k != -1:
            ocr_result.append(DS.OCRResult(DS.Rect(bx, by, bw, bh), max_k))

    sorted_ocr_results = sorted(ocr_result, key=rect_sort)
    cv2.imshow("image", image)
    return sorted_ocr_results


def getGameMapFromOcrResult(ocr_results):
    game_map = [[0 for _ in range(kGameCol)] for _ in range(kGameRow)]
    rect_map = [[DS.Rect(0, 0, 0, 0) for _ in range(kGameCol)] for _ in range(kGameRow)]
    for i in range(len(ocr_results)):
        game_map[int(i / kGameCol)][i % kGameCol] = ocr_results[i].v
        rect_map[int(i / kGameCol)][i % kGameCol] = ocr_results[i].rect
    return game_map, rect_map


ocrResults = get_ocr_result(screen_shot_image)

for i in range(len(ocrResults)):
    print("{} ".format(ocrResults[i].v), end="")

if len(ocrResults) < kGameCol * kGameRow:
    print("数字OCR识别失败！")
    exit(-1)

gameMap, rectMap = getGameMapFromOcrResult(ocrResults)


def debugInfo(head_text, vector2):
    print(head_text)
    for row in range(len(vector2)):
        for col in range(len(vector2[row])):
            print(vector2[row][col], " ", end="")
        print("")


def getPrefixSum2(map2):
    sumMap = [[0 for _ in range(kGameCol)] for _ in range(kGameRow)]
    for row in range(kGameRow):
        for col in range(kGameCol):
            sumMap[row][col] = map2[row][col]
            top_value = sumMap[row - 1][col] if row > 0 else 0
            left_value = sumMap[row][col - 1] if col > 0 else 0
            top_left_value = sumMap[row - 1][col - 1] if row > 0 and col > 0 else 0
            sumMap[row][col] = sumMap[row][col] + top_value + left_value - top_left_value
    return sumMap


def getSum10Rects(sum_map2, s_col, s_row):
    rects = []
    for row in range(s_row, kGameRow):
        for col in range(s_col, kGameCol):
            top_value = sum_map2[s_row - 1][col] if s_row > 0 else 0
            left_value = sum_map2[row][s_col - 1] if s_col > 0 else 0
            top_left_value = sum_map2[s_row - 1][s_col - 1] if s_row > 0 and s_col > 0 else 0
            tmp_sum = sum_map2[row][col] - top_value - left_value + top_left_value
            if tmp_sum == kGameSum:
                rects.append(DS.Rect(s_col, s_row, col - s_col + 1, row - s_row + 1))
            else:
                if tmp_sum > kGameSum:
                    break
    return rects


def resetZero(map2, rect):
    res = 0 # 重置为0的个数
    for row in range(rect.y, rect.y + rect.h):
        for col in range(rect.x, rect.x + rect.w):
            if map2[row][col] == 0:
                continue
            map2[row][col] = 0
            res += 1
    return res


def getSteps(gameMaps, score, steps):
    if score > 100:
        return True
    sumGameMap = getPrefixSum2(gameMaps)
    # debugInfo("gameMaps: ", gameMaps)
    if sumGameMap[kGameRow - 1][kGameCol - 1] == 0:
        return True
    for row in range(kGameRow):
        for col in range(kGameCol):
            if gameMaps[row][col] == 0:
                continue
            sum10_rects = getSum10Rects(sumGameMap, col, row)
            for rect in sum10_rects:
                steps.append(rect)
                tmp_maps = gameMap
                zero_count = resetZero(tmp_maps, rect)
                if getSteps(tmp_maps, score + zero_count, steps):
                    return True
                steps.pop()
    return False


# 模拟触摸拖拽事件
def sendDragEvent(device, start_x, start_y, end_x, end_y, duration_ms):
    cmd = f"input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}"
    device.shell(cmd)
# debugInfo("Game Map:", gameMap)


result_steps = []
result_steps_pixel = []
if getSteps(gameMap, 0, result_steps):
    print("找到了一组解")
    for i in range(len(result_steps)):
        bxi = result_steps[i].x
        byi = result_steps[i].y
        exi = result_steps[i].w + bxi - 1
        eyi = result_steps[i].h + byi - 1
        # print("Rect({}, {}, {}, {})".format(bxi, byi, exi, eyi))
        start_point_x, start_point_y = rectMap[byi][bxi].center()
        end_point_x, end_point_y = rectMap[eyi][exi].center()
        # print("Start({}, {}), End({}, {})".format(start_point_x, start_point_y, end_point_x, end_point_y))
        result_steps_pixel.append(DS.Rect(start_point_x, start_point_y, end_point_x - start_point_x, end_point_y - start_point_y))
        sendDragEvent(device, start_point_x, start_point_y, end_point_x, end_point_y, 200)
else:
    print("没有找到解")

