# -*- coding: utf-8 -*-
# @Time     : 2023-02-21 20:17
# @Author   : Big Cheng
# @FileName : pc端ui界面.py
import os
import socket
import sys
import winreg
import time
import io

import cv2
from PIL import Image
import numpy as np
from PySide6.QtCore import QTimer, QThread, QSettings
from PySide6.QtGui import QIcon, Qt, QImage, QPixmap
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGroupBox, QHBoxLayout, QStyle, QVBoxLayout, \
    QStackedLayout, QLineEdit, QComboBox, QMessageBox, QFileDialog
from detection import detector

import PySide6
import requests

dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

CAPTURE_IMAGE_DATA = None
SAVE_VIDEO_PATH = ""
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
udp_socket.bind(('', 9090))
detector = detector()
http_addr = "http://localhost:9999/record/"


# 通信线程
class ChatThread(QThread):
    def __init__(self):
        super().__init__()
        # 保存esp的ip信息
        self.esp_addr = ()  # 单个连接
        # 用于通信的socket和端口
        self.chat_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.chat_sock.bind(('', 9091))

    def run(self):
        print('通信线程已启动...')
        while True:
            data, IP = self.chat_sock.recvfrom(1000)
            self.esp_addr = IP
            data = data.decode()
            print('接收到信息：' + data)

    def sendStrtoEsp(self, msg):
        self.chat_sock.sendto(msg.encode('utf-8'), self.esp_addr)
        print('通信线程信息已发送:' + msg)

    def sendHttptoCloud(self, url, operation):
        try:
            get_addr = http_addr + url + socket.gethostname() + "&&" + operation
            return requests.get(get_addr)
        except:
            pass

    def sendtoCloud(self, img_bytes):
        # addr = ("139.224.133.71", 9090)
        addr = ("127.0.0.1", 8888)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sent = s.sendto(img_bytes, addr)

class CaptureThread(QThread):
    def __init__(self, ip, port, chat_thread):
        super().__init__()
        # self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # self.udp_socket.bind((ip, port))
        self.chat_thread = chat_thread
        # 设置运行的标志
        # self.s.sendto('app'.encode('utf-8'), ('139.224.133.71', 9090))
        self.run_flag = True
        self.record_flag = False
        self.auto_flag = False  # 是否开启自动追踪
        self.addr = (ip, port)
        # self.s.bind(('', 9090))

    def run(self):
        global CAPTURE_IMAGE_DATA

        # self.s.sendto("apps".encode('utf-8'), self.addr)
        while self.run_flag:
            data, ip = udp_socket.recvfrom(30000)
            print('接受到数据...')
            bytes_stream = io.BytesIO(data)
            image = Image.open(bytes_stream)
            img = np.asarray(image)
            if self.auto_flag:  # 开启自动追踪
                img, dir = detector.auto_trace(img)
                if len(dir) > 0:
                    self.chat_thread.sendStrtoEsp(str([dir, 5, 5]))
            else:
                detector.detect(img)

            if self.record_flag:  # 开始录制视频
                # 转换数据格式，便于存储视频文件
                img_2 = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # ESP32采集的是RGB格式，要转换为BGR（opencv的格式）
                self.chat_thread.sendtoCloud(data)
                self.mp4_file.write(img_2)

            # PySide显示不需要转换，所以直接用img
            temp_image = QImage(img.flatten(), 480, 320, QImage.Format.Format_RGB888)
            temp_pixmap = QPixmap.fromImage(temp_image)
            CAPTURE_IMAGE_DATA = temp_pixmap  # 暂时存储udp接收到的1帧视频画面

        # 结束后 关闭套接字
        # self.udp_socket.close()
        print('已关闭套接字')

    def stop_run(self):
        self.run_flag = False
        self.record_flag = False
        try:
            self.mp4_file.release()
        except Exception as ret:
            pass

    def stop_record(self):
        self.mp4_file.release()
        self.record_flag = False

    def start_record(self):
        # 设置视频的编码解码方式avi
        video_type = cv2.VideoWriter_fourcc(*'XVID')  # 视频存储的格式
        # 保存的位置，以及编码解码方式，帧率，视频帧大小
        file_name = "{}.avi".format(time.time())
        file_path_name = os.path.join(SAVE_VIDEO_PATH, file_name)
        self.mp4_file = cv2.VideoWriter(file_path_name, video_type, 5, (480, 320))
        self.record_flag = True




class ShowCaptureVideoWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        # 用来显示画面的QLabel
        self.video_label = QLabel("选择顶部的操作按钮...")
        self.video_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.video_label.setScaledContents(True)
        layout.addWidget(self.video_label)

        self.setLayout(layout)


class VideoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("esp32-cam远程摄像头监控")
        self.setWindowIcon(QIcon('./images/logo.png'))
        self.resize(666, 666)

        # 选择本电脑IP
        camera_label = QLabel("选择本电脑IP：")

        # ip列表
        # 获取本地电脑的ip地址列表
        hostname, alias_list, ip_addr_list = socket.gethostbyname_ex(socket.gethostname())
        # print(hostname)  # DESKTOP
        # print(alias_list)  # []
        # print(ip_addr_list)  # ['192.168.47.1', '192.168.208.1', '192.168.31.53']
        ip_addr_list.insert(0, "0.0.0.0")
        self.combox = QComboBox()
        self.combox.addItems(ip_addr_list)
        self.ip_addr_list = ip_addr_list

        # 本地端口
        port_label = QLabel("本地端口：")
        self.port_edit = QLineEdit("9090")

        g_1 = QGroupBox("监听信息")
        g_1.setFixedHeight(60)
        g_1_h_layout = QHBoxLayout()
        g_1_h_layout.addWidget(camera_label)
        g_1_h_layout.addWidget(self.combox)
        g_1_h_layout.addWidget(port_label)
        g_1_h_layout.addWidget(self.port_edit)
        g_1.setLayout(g_1_h_layout)

        # 启动通信
        self.chat_thread = ChatThread()
        self.chat_thread.daemon = True
        self.chat_thread.start()

        # 启动显示
        self.camera_open_close_btn = QPushButton(QIcon("./images/shexiangtou.png"), "启动显示")
        self.camera_open_close_btn.clicked.connect(self.camera_open_close)

        self.record_video_btn = QPushButton(QIcon("./images/record.png"), "开始录制")
        self.record_video_btn.clicked.connect(self.recorde_video)

        save_video_path_setting_btn = QPushButton(QIcon("./images/folder.png"), "设置保存路径")
        save_video_path_setting_btn.clicked.connect(self.save_video_path_setting)

        up_control_btn = QPushButton(QIcon("./images/folder.png"), "↑")
        up_control_btn.clicked.connect(self.ask_cam_rise)
        down_control_btn = QPushButton(QIcon("./images/folder.png"), "↓")
        down_control_btn.clicked.connect(self.ask_cam_down)
        left_control_btn = QPushButton(QIcon("./images/folder.png"), "←")
        left_control_btn.clicked.connect(self.ask_cam_left)
        right_control_btn = QPushButton(QIcon("./images/folder.png"), "→")
        right_control_btn.clicked.connect(self.ask_cam_right)
        self.auto_control_btn = QPushButton(QIcon("./images/folder.png"), "auto")
        self.auto_control_btn.clicked.connect(self.auto_trace)

        g_2 = QGroupBox("功能操作")
        g_2.setFixedHeight(60)
        g_2_h_layout = QHBoxLayout()
        g_2_h_layout.addWidget(self.camera_open_close_btn)
        g_2_h_layout.addWidget(self.record_video_btn)
        g_2_h_layout.addWidget(save_video_path_setting_btn)
        g_2.setLayout(g_2_h_layout)

        g_3 = QGroupBox("转向控制")
        g_3.setFixedHeight(60)
        g_3_h_layout = QHBoxLayout()
        g_3_h_layout.addWidget(up_control_btn)
        g_3_h_layout.addWidget(down_control_btn)
        g_3_h_layout.addWidget(left_control_btn)
        g_3_h_layout.addWidget(right_control_btn)
        g_3_h_layout.addWidget(self.auto_control_btn)
        g_3.setLayout(g_3_h_layout)

        # --------- 整体布局 ---------
        h_layout = QHBoxLayout()
        h_layout.addWidget(g_1)
        h_layout.addWidget(g_2)
        h_layout.addWidget(g_3)
        h_layout.addStretch(1)

        v_layout = QVBoxLayout()
        v_layout.addLayout(h_layout)

        # 创建底部的显示区域
        self.stacked_layout_capture_view = ShowCaptureVideoWidget()
        v_layout.addWidget(self.stacked_layout_capture_view)

        self.setLayout(v_layout)
        # 定时刷新视频画面
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_video_image)
        self.load_time = 0
        self.load_time_all = 0

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.s.bind(('', 9090))

    def camera_open_close(self):
        """启动创建socket线程，用来接收显示数据"""

        addr = ("139.224.133.71", 9090)
        msg = "apps".encode('utf-8')
        # sent = s.sendto(msg, addr)
        if self.camera_open_close_btn.text() == "启动显示":
            # ip = self.combox.currentText()
            ip = ''
            try:
                port = 9090
                # port = int(self.port_edit.text())
                self.chat_thread.sendStrtoEsp('open')
                res = self.chat_thread.sendHttptoCloud("update/", "打开相机")

            except Exception as ret:
                QMessageBox.about(self, '警告', '端口设置错误！！！')
                return

            self.thread = CaptureThread(ip, port, self.chat_thread)
            self.thread.daemon = True
            self.thread.start()
            self.timer.start(100)  # 设置计时间隔并启动
            self.camera_open_close_btn.setText("关闭显示")
        else:
            res = self.chat_thread.sendHttptoCloud("update/", "关闭录制")
            self.chat_thread.sendStrtoEsp('stop')
            self.camera_open_close_btn.setText("启动显示")
            self.timer.stop()
            self.stacked_layout_capture_view.video_label.clear()
            self.thread.stop_run()
            self.record_video_btn.setText("开始录制")

    def show_video_image(self):
        if CAPTURE_IMAGE_DATA:
            self.stacked_layout_capture_view.video_label.setPixmap(CAPTURE_IMAGE_DATA)
        else:
            if time.time() - self.load_time >= 1:
                self.load_time = time.time()
                self.load_time_all += 1
                self.stacked_layout_capture_view.video_label.setText("摄像头加载中...{}".format(self.load_time_all))

    def ask_cam_rise(self, angle=10, speed=10):
        res = self.chat_thread.sendHttptoCloud("update/", "up")
        self.chat_thread.sendStrtoEsp(str(['up', angle, speed]))

    def ask_cam_down(self, angle=10, speed=10):
        res = self.chat_thread.sendHttptoCloud("update/", "down")
        self.chat_thread.sendStrtoEsp(str(['down', angle, speed]))

    def ask_cam_left(self, angle=10, speed=10):
        res = self.chat_thread.sendHttptoCloud("update/", "left")
        self.chat_thread.sendStrtoEsp(str(['left', angle, speed]))

    def ask_cam_right(self, angle=10, speed=10):
        res = self.chat_thread.sendHttptoCloud("update/", "right")
        self.chat_thread.sendStrtoEsp(str(['right', angle, speed]))

    def ask_cam_move(self, angle=10, speed=10):
        self.chat_thread.sendStrtoEsp(str([angle, speed]))

    # 开启自动追踪功能
    def auto_trace(self):
        print('auto_trace')
        res = self.chat_thread.sendHttptoCloud("update/", "start auto trace")
        if self.auto_control_btn.text() == 'auto':
            self.auto_control_btn.setText("停止追踪")
            self.thread.auto_flag = True
        else:
            self.auto_control_btn.setText("auto")
            self.thread.auto_flag = False

    @staticmethod
    def get_desktop():
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
        return winreg.QueryValueEx(key, "Desktop")[0]

    def save_video_path_setting(self):
        """视频保存路径"""
        global SAVE_VIDEO_PATH
        res = self.chat_thread.sendHttptoCloud("update/", "保存视频")
        if SAVE_VIDEO_PATH:
            last_path = QSettings().value("LastFilePath")
        else:
            last_path = self.get_desktop()

        path_name = QFileDialog.getExistingDirectory(self, '请选择保存视频的路径', last_path)
        if not path_name:
            return

        SAVE_VIDEO_PATH = path_name

    def recorde_video(self):
        """录制视频"""
        if self.camera_open_close_btn.text() == "启动显示":
            QMessageBox.about(self, '警告', '请先启动显示，然后再开始录制！！！')
            return

        if not SAVE_VIDEO_PATH:
            QMessageBox.about(self, '警告', '请先配置视频保存路径！！！')
            return

        if self.record_video_btn.text() == "开始录制":
            self.record_video_btn.setText("停止录制")
            self.thread.start_record()
        else:
            self.record_video_btn.setText("开始录制")
            self.thread.stop_record()


def updateRecord(operation):
    try:
        get_addr = http_addr + "update/" + socket.gethostname() + "&&" + operation
        return requests.get(get_addr)
    except:
        pass


def hello():
    print('hello')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    video_window = VideoWindow()
    video_window.show()
    app.exec()
