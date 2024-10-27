import sys
import socket
from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QDialog, QFormLayout, QLineEdit, \
    QHBoxLayout
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QPolygonF

address = "192.168.4.1"
port = "8080"
scale = "1000000"

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(300, 200)
        self.layout = QFormLayout(self)
        self.ip_input = QLineEdit("192.168.4.1")
        self.ip_input.setPlaceholderText("IP Address")
        self.layout.addRow("IP Address:", self.ip_input)
        self.port_input = QLineEdit("8080")
        self.port_input.setPlaceholderText("Port")
        self.layout.addRow("Port:", self.port_input)
        self.scale_input = QLineEdit("1000000")
        self.scale_input.setPlaceholderText("Scale")
        self.layout.addRow("Scale:", self.scale_input)
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_settings)
        self.layout.addRow(self.save_button)

        # 实例变量用于存储设置
        self.address = ""
        self.port = ""
        self.scale = ""

    def save_settings(self):
        # 更新实例变量
        self.address = self.ip_input.text()
        self.port = self.port_input.text()
        self.scale = self.scale_input.text()
        self.accept()

    def get_settings(self):
        # 返回实例变量
        return self.address, self.port, self.scale


class GNSSWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 假设这个列表存储了轨迹点坐标 (x, y)
        self.trajectories = [
            ((300, 300), (300, 250), (300, 200), (300, 150), (300, 100), (300, 50)),  # 线段1
            ((300, 300), (300, 250), (300, 200), (350, 200), (400, 200), (450, 200), (500, 200), (550, 200) ),  # 线段2
            ((300, 300), (300, 250), (300, 200), (350, 200), (400, 200), (450, 150), (450, 100), (450, 50)),  # 线段2
        ]
        #self.trajectory_points = [(300, 300), (300, 250), (300, 200), (300, 150), (300, 100), (300, 50)]  # 示例轨迹点

        # 初始化窗口设置
        self.setWindowTitle("GNSS ToolKit")
        self.resize(600, 600)

        # 存储轨迹和中心位置
        self.trajectory = []
        self.current_position = None
        self.center_longitude = None
        self.center_latitude = None
        self.scale = 1000000  # 默认缩放比例
        # 创建界面布局
        layout = QVBoxLayout()
        self.selected_trajectory = None  # 用于记录选中的轨迹
        # 创建一个水平布局用于放置连接和设置按钮
        button_layout = QHBoxLayout()

        # 连接/断开连接按钮
        self.connect_button = QPushButton('Connect', self)
        self.connect_button.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_button)

        # 设置按钮
        self.settings_button = QPushButton('Settings', self)
        self.settings_button.clicked.connect(self.open_settings)
        button_layout.addWidget(self.settings_button)

        # 将按钮布局添加到主布局中
        layout.addLayout(button_layout)

        # 在连接按钮和标签之间添加弹性空间，以将标签移动到窗口底部
        layout.addStretch()

        # 数据显示标签
        self.data_label = QLabel('Data: None', self)
        layout.addWidget(self.data_label)

        self.setLayout(layout)

        # 启动一个线程用于接收数据
        self.receiver_thread = None
        self.client_socket = None
        self.current_frame = None  # 当前捕捉到的帧.3

        self.loading_timer = QTimer(self)  # 用于计时3秒
        #self.loading_timer.timeout.connect(self.start_recognition_thread)  # 设置超时信号连接到识别线程启动方法

    def toggle_connection(self):
        if self.receiver_thread is None or not self.receiver_thread.is_alive():
            # 尝试连接
            self.connect_button.setText('Disconnect')
            self.start_connection_thread()
        else:
            # 断开连接
            self.disconnect_from_server()
            self.connect_button.setText('Connect')  # 更新按钮文本为 "Connect"


    def start_connection_thread(self):
        # 启动连接线程
        thread = Thread(target=self.connect_to_server)
        thread.start()

    def connect_to_server(self):
        print("开始连接:", address, port, scale)
        if not address or not port.isdigit():
            self.data_label.setText("Please set a valid IP and port.")
            return

        self.scale = int(scale) if scale.isdigit() else self.scale  # 更新缩放比例

        try:
            # 创建一个新的 socket 连接
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((address, int(port)))  # 使用设置的IP和端口

            # 成功连接后，更新标签并重置缓冲区
            self.data_label.setText('Connected!')

            # 启动接收数据线程
            self.receiver_thread = Thread(target=self.receive_data)
            self.receiver_thread.daemon = True
            self.receiver_thread.start()
        except Exception as e:
            self.client_socket = None
            self.data_label.setText(f'Connection failed: {str(e)}')

    def disconnect_from_server(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            self.receiver_thread = None
            self.data_label.setText('Disconnected!')

    def receive_data(self):
        try:
            while True:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break  # 如果没有数据，则退出循环
                self.update_position(data)
        except Exception as e:
            self.data_label.setText(f'Error: {str(e)}')

    def update_position(self, data):
        try:
            print("Received: ", data)
            # 假设数据格式为 "longitude,latitude,result"
            longitude, latitude, result = data.split(',')
            longitude = float(longitude)
            latitude = float(latitude)

            # 如果是第一次接收数据，设置中心位置
            if self.center_longitude is None and self.center_latitude is None:
                self.center_longitude = longitude
                self.center_latitude = latitude
                # 更新当前位置
                self.current_position = (longitude, latitude)
                self.data_label.setText(f"Center set at Longitude: {self.center_longitude}, Latitude: {self.center_latitude}")
            else:
                # 计算相对位置
                longitude -= self.center_longitude
                latitude -= self.center_latitude
                print("相对位置是", longitude, latitude)
                # 更新当前位置
                self.current_position = (longitude, latitude)
                self.trajectory.append(self.current_position)
                print("新增点: ", self.current_position)
            # 更新标签显示数据
            self.data_label.setText(
                f"Longitude: {longitude + self.center_longitude}, Latitude: {latitude + self.center_latitude}, Result: {result}")

            # 处理转向信息
            if result == "1":
                self.selected_trajectory = 1  # 记录选中的轨迹
                self.data_label.setText(self.data_label.text() + " - Turn Left")
            elif result == "2":
                self.data_label.setText(self.data_label.text() + " - Turn Right")
                self.selected_trajectory = 2  # 记录选中的轨迹
            else:
                self.data_label.setText(self.data_label.text() + " - Straight")

            # 触发界面重绘
            self.update()
        except Exception as e:
            self.data_label.setText(f'Error: {str(e)}')

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        if settings_dialog.exec_() == QDialog.Accepted:
            # 获取设置
            ip, port, scale = settings_dialog.get_settings()
            self.data_label.setText(f"Settings saved: IP={ip}, Port={port}, Scale={scale}")

            # 更新实例变量
            self.address = ip
            self.port = port
            self.scale = scale

    def paintEvent(self, event):
        painter = QPainter(self)
        # 绘制网格背景
        self.draw_grid(painter)
        self.draw_trajectories(painter)
        # 放大比例因子
        scale = self.scale  # 使用设置的缩放比例
        # 绘制轨迹线段，仅在有两个或更多点时绘制
        if len(self.trajectory) >= 2 and self.current_position:  # 确保至少有两个点才能绘制线段
            pen = QPen(Qt.gray, 2)  # 使用灰色画笔，宽度为2
            painter.setPen(pen)
            # 将轨迹点转换为 QPointF 对象
            polyline = [QPointF(point[0] * scale + self.width() // 2,
                                point[1] * scale + self.height() // 2) for point in self.trajectory]

            painter.drawPolyline(QPolygonF(polyline))  # 绘制线段

        # 绘制轨迹点
        if self.trajectory:
            pen = QPen(Qt.red, 3)  # 使用红色画笔，宽度为3
            painter.setPen(pen)
            for point in self.trajectory:
                x = int(point[0] * scale + self.width() // 2)
                y = int(point[1] * scale + self.height() // 2)
                painter.drawPoint(x, y)

        # 绘制当前位置
        if self.current_position:
            pen = QPen(Qt.blue, 5)
            painter.setPen(pen)
            painter.drawPoint(int(self.current_position[0] * scale + self.width() // 2),
                              int(self.current_position[1] * scale + self.height() // 2))
            # 绘制转向指示（箭头）
            self.draw_turn_indicator(painter)

    def draw_turn_indicator(self, painter):
        if self.current_position is not None:
            # 设置箭头的颜色和大小
            pen = QPen(Qt.green, 2)  # 减小线宽
            painter.setPen(pen)

            # 根据 result 绘制箭头
            # 假设 result 是在 update_position 方法中更新的
            if 'Turn Left' in self.data_label.text():
                # 绘制左转箭头
                arrow_length = 0.00001  # 调整箭头长度
                arrow_width = 0.000005  # 调整箭头宽度

                # 绘制箭头的主线
                painter.drawLine(
                    int(self.current_position[0] * self.scale + self.width() // 2),
                    int(self.current_position[1] * self.scale + self.height() // 2),
                    int((self.current_position[0] - arrow_length) * self.scale + self.width() // 2),
                    int(self.current_position[1] * self.scale + self.height() // 2)
                )
                # 绘制箭头的两侧
                painter.drawLine(
                    int((self.current_position[0] - arrow_length) * self.scale + self.width() // 2),
                    int(self.current_position[1] * self.scale + self.height() // 2),
                    int((self.current_position[0] - arrow_length) * self.scale + self.width() // 2),
                    int((self.current_position[1] + arrow_width) * self.scale + self.height() // 2)
                )
                painter.drawLine(
                    int((self.current_position[0] - arrow_length) * self.scale + self.width() // 2),
                    int(self.current_position[1] * self.scale + self.height() // 2),
                    int((self.current_position[0] - arrow_length) * self.scale + self.width() // 2),
                    int((self.current_position[1] - arrow_width) * self.scale + self.height() // 2)
                )
            elif 'Turn Right' in self.data_label.text():
                # 绘制右转箭头
                arrow_length = 0.00001  # 调整箭头长度
                arrow_width = 0.000005  # 调整箭头宽度

                # 绘制箭头的主线
                painter.drawLine(
                    int(self.current_position[0] * self.scale + self.width() // 2),
                    int(self.current_position[1] * self.scale + self.height() // 2),
                    int((self.current_position[0] + arrow_length) * self.scale + self.width() // 2),
                    int(self.current_position[1] * self.scale + self.height() // 2)
                )
                # 绘制箭头的两侧
                painter.drawLine(
                    int((self.current_position[0] + arrow_length) * self.scale + self.width() // 2),
                    int(self.current_position[1] * self.scale + self.height() // 2),
                    int((self.current_position[0] + arrow_length) * self.scale + self.width() // 2),
                    int((self.current_position[1] + arrow_width) * self.scale + self.height() // 2)
                )
                painter.drawLine(
                    int((self.current_position[0] + arrow_length) * self.scale + self.width() // 2),
                    int(self.current_position[1] * self.scale + self.height() // 2),
                    int((self.current_position[0] + arrow_length) * self.scale + self.width() // 2),
                    int((self.current_position[1] - arrow_width) * self.scale + self.height() // 2)
                )

    def draw_grid(self, painter):
        pen = QPen(QColor(0, 0, 0, 100), 1, Qt.DotLine)  # 设置网格颜色和样式
        painter.setPen(pen)

        # 获取窗口的宽高
        width = self.width()
        height = self.height()

        # 设置网格间距
        grid_spacing = 50

        # 绘制水平网格线
        for y in range(0, height, grid_spacing):
            painter.drawLine(0, y, width, y)

        # 绘制垂直网格线
        for x in range(0, width, grid_spacing):
            painter.drawLine(x, 0, x, height)

        # 绘制X、Y轴
        painter.drawLine(width // 2, 0, width // 2, height)  # Y轴
        painter.drawLine(0, height // 2, width, height // 2)  # X轴



    def draw_trajectories(self, painter):
        # 遍历每个轨迹，绘制连接的多个点
        for i, trajectory in enumerate(self.trajectories):
            if i == self.selected_trajectory:
                pen = QPen(QColor(0, 0, 255), 2)  # 选中状态：蓝色
            else:
                color = QColor(64, 64, 64) if i == 0 else QColor(64, 64, 64) if i == 1 else QColor(64, 64, 64)
                pen = QPen(color, 2)  # 正常状态
            painter.setPen(pen)

            # 遍历每个点，绘制连接的线段
            for j in range(len(trajectory) - 1):
                start_point = trajectory[j]
                end_point = trajectory[j + 1]
                painter.drawLine(int(start_point[0]), int(start_point[1]), int(end_point[0]), int(end_point[1]))

            # 可选：绘制每个点的小圆点
            for point in trajectory:
                painter.drawEllipse(int(point[0]) - 3, int(point[1]) - 3, 6, 6)  # 标记点

    def mousePressEvent(self, event):
        # 获取点击位置
        click_pos = event.pos()

        for i, trajectory in enumerate(self.trajectories):
            for j in range(len(trajectory) - 1):
                start_point = QPointF(trajectory[j][0], trajectory[j][1])
                end_point = QPointF(trajectory[j + 1][0], trajectory[j + 1][1])
                if self.is_point_near_line(click_pos, start_point, end_point):
                    self.selected_trajectory = i  
                    self.update() 
                    return

    def is_point_near_line(self, point, line_start, line_end, threshold=10):
        line_vec = line_end - line_start
        point_vec = point - line_start
        line_length = line_vec.manhattanLength()

        if line_length == 0:
            return False

        t = max(0, min(1, QPointF.dotProduct(point_vec, line_vec) / line_length ** 2))
        closest_point = line_start + t * line_vec
        distance = (closest_point - point).manhattanLength()

        return distance <= threshold  # 判断距离是否小于某个阈值


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GNSSWindow()
    window.show()
    sys.exit(app.exec_())
