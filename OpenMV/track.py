import sensor, image, time, math
from pyb import UART, LED

# 初始化相机
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
clock = time.clock()
sensor.set_auto_gain(True)  # 开启自动增益
sensor.set_auto_whitebal(True)  # 开启自动白平衡

ROI_top = (100, 0, 100, 70)
ROI_bottom = (50, 100, 200, 70)

uart = UART(3, 115200)   # 定义串口3变量
uart.init(115200, bits=8, parity=None, stop=1)  # 初始化串口
delaytime = 0

qr_detected = False
qr_data = None
use_qr = True
turn = 0x00

while(True):
    clock.tick()
    img = sensor.snapshot()

    # 使用 find_line_segments() 函数检测上半段的线段
    line_segments_top = img.find_line_segments(roi=ROI_top, merge_distance=1, max_theta_diff=10)

    # 使用 find_line_segments() 函数检测下半段的线段
    line_segments_bottom = img.find_line_segments(roi=ROI_bottom, merge_distance=10, max_theta_diff=15)

    has_straight = False
    has_right_turn = False
    has_left_turn = False
    left_line_count = 0
    right_line_count = 0

    # 检测二维码并解码
    qrcodes = img.find_qrcodes()
    if qrcodes:
        qr_detected = True
        for qrcode in qrcodes:
            img.draw_rectangle(qrcode.rect(), color=(255, 0, 0))  # 红色矩形框住二维码
            img.draw_string(qrcode.rect()[0], qrcode.rect()[1] - 10, qrcode.payload(), color=(0, 255, 0))  # 显示二维码内容
            qr_data = qrcode.payload()  # 获取二维码内容

    # 处理上半段检测到的线段
    for segment in line_segments_top:
        theta = segment.theta()
        line = segment.line()
        if 10 < theta < 40:
            has_straight = True
            img.draw_line(line, color=(0, 255, 0))  # 绿色直线
        elif 70 > theta > 41:
            has_right_turn = True
            img.draw_line(line, color=(255, 0, 0))  # 红色右转
        elif 0 < theta < 5:
            has_left_turn = True
            img.draw_line(line, color=(0, 0, 255))  # 蓝色左转


    # 处理下半段检测到的线段
    for segment in line_segments_bottom:
        theta = segment.theta()
        line = segment.line()
        mid_x = (line[0] + line[2]) // 2
        if 0 < theta < 40 or 160 < theta < 180:
            img.draw_line(line, color=(255, 255, 0))  # 黄色直线
            if mid_x < (ROI_bottom[0] + ROI_bottom[2]) // 2:
                left_line_count += 1
            else:
                right_line_count += 1



    # 根据检测结果显示信息
    result_text = "Null"
    if has_straight and has_right_turn:
        result_text = "straight and right"
    elif has_straight and has_left_turn:
        result_text = "straight and left_turn"
    elif has_straight:
        result_text = "straight"
    elif has_right_turn:
        result_text = "right"

    img.draw_string(210, 200, result_text, color=(255, 0, 0), scale=1)  # 显示检测结果
    img.draw_rectangle(ROI_bottom[0], ROI_bottom[1], ROI_bottom[2], ROI_bottom[3], color=(0, 255, 0), thickness=1)  # 绘制ROI

    # 显示左半边和右半边的直线数量
    count_text = "Left: {}, Right: {}".format(left_line_count, right_line_count)
    img.draw_string(10, 200, count_text, color=(255, 0, 0), scale=1)

    # 如果检测到了二维码
    if qr_detected:
        print("QR Code detected: ", qr_data)
        # 根据二维码内容修改发送的 FH 数据
        if use_qr:
            if qr_data == "0x000001":
                turn = 0x01  # 左转的指令
            elif qr_data == "0x000002":
                turn = 0x02  # 右转的指令
            else :
                turn = 0x00  # 默认的指令
        else:
            if left_line_count > right_line_count:
                turn = 0x01
                print("result")
            elif left_line_count <= right_line_count:
                turn = 0x02
        # 重置标志位
        qr_detected = False

    # 如果没有二维码，则正常发送默认数据
    delaytime += 1
    if delaytime > 10 and not qr_detected:
        #FH = bytearray([0xAA, 0x01, 0x55])
        FH = bytearray([0xAA, turn, 0x55])
        print(turn)
        uart.write(FH)
        print(FH)
        delaytime = 0
