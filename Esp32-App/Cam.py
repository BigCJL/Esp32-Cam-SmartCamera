# -*- coding: utf-8 -*-
# @Time     : 2023-03-07 10:58
# @Author   : Big Cheng
# @FileName : Cam.py
import socket
import network
import camera
import time
import _thread
from machine import Pin, PWM
# led灯亮灭
led = Pin(4, Pin.OUT)
led.value(0)
# 舵机类
addr = ('192.168.233.226', 9090)  # ip修改这里, 子网下重复连接会动态变化
chat_addr = ('192.168.233.226', 9091)  # 通信端口和视频流端口

class Sg90:
    def __init__(self):
        self.p2 = PWM(Pin(2))  # 上下
        self.p2.freq(50)
        self.p12 = PWM(Pin(12))  # 左右
        self.p12.freq(50)
        # 0度   p2.duty_u16(1638)  顺时针90(上摇)
        # 90度  p2.duty_u16(4915)  逆时针90（下摇）
        # 180度 p2.duty_u16(8192)  逆时针180
        # self.reset()

    # 获取当前纵向舵机的pwm信号占空比
    def getVerticalRatio(self):
        return self.p2.duty_u16()

    def reset(self):
        # self.p2.duty_u16(4096)
        time.sleep(1)
        self.p12.duty_u16(5000)
        time.sleep(1)
        print("已复位, 初始占空比:50%")

    def down(self, angle, speed=10):
        cur = self.getVerticalRatio()
        # gap = int((8192 - 1638) / 180 * angle)
        gap = int(36 * angle)
        print("下摇中...")
        print("当前频率:" + str(cur))
        # time.sleep(2)
        for i in range(cur, cur + gap, speed):
            self.p2.duty_u16(i)
            time.sleep_ms(10)
        print("下摇{}°结束".format(angle))

    def up(self, angle, speed=10):  # 上摇到底
        cur = self.p2.duty_u16()
        gap = int(36 * angle)
        print("上摇中...")
        print("当前频率:" + str(cur))
        # time.sleep(2)
        for i in range(cur, cur - gap, -speed):
            self.p2.duty_u16(i)
            time.sleep_ms(10)
        print("上摇{}°结束".format(angle))

    def left(self, angle, speed=10):
        cur = self.p12.duty_u16()
        gap = int(36 * angle)
        print("左旋中...")
        print("当前频率:" + str(cur))
        # time.sleep(2)
        for i in range(cur, cur - gap, -speed):
            self.p12.duty_u16(i)
            time.sleep_ms(10)
        print("左旋{}°结束".format(angle))

    def right(self, angle, speed=10):
        cur = self.p12.duty_u16()
        print("右旋中...")
        print("当前频率:" + str(cur))
        for i in range(cur, cur + angle * 36, speed):
            self.p12.duty_u16(i)
            time.sleep_ms(10)
        print("右旋{}°结束".format(angle))

class Cam:
    def __init__(self):
        self.wlan = network.WLAN(network.STA_IF)
        self.addr = addr  # ip修改这里, 子网下重复连接会动态变化
        self.chat_addr = chat_addr  # 通信端口和视频流端口
        self.ssid = 'Xiaomi12X'
        self.pwd = '123456789'
        # socket UDP 的创建
        self.chat_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.run_flag = False
        self.thread_cam = _thread

    def connect_wlan(self):
        # 连接wifi
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        while not wlan.isconnected():
            print('connecting to network...')
            wlan.connect(self.ssid, self.pwd)  # 阻塞？ 可以考虑异步

            if wlan.isconnected():
                break
        if wlan.isconnected():
            led.value(1)
            time.sleep(0.1)
            led.value(0)
            print('网络配置:', wlan.ifconfig())

    def init_camera(self):
        # 摄像头初始化
        try:
            camera.init(0, format=camera.JPEG)
        except Exception as e:
            camera.deinit()
            camera.init(0, format=camera.JPEG)
        camera.flip(0)
        camera.mirror(1)
        camera.framesize(camera.FRAME_HVGA)
        camera.speffect(camera.EFFECT_NONE)
        camera.whitebalance(camera.WB_HOME)
        camera.saturation(0)
        camera.brightness(0)
        camera.contrast(0)
        camera.quality(10)

    def sendStrtoClient(self, msg):
        self.chat_sock.sendto(msg.encode('utf-8'), self.chat_addr)
        print('已发送信息:' + msg)

    def loop(self):
        self.connect_wlan()
        self.sendStrtoClient('esp')  # 让对端接收到当前在线的摄像头地址信息
        sg90 = Sg90()
        sg90.reset()
        while True:
            data, IP = self.chat_sock.recvfrom(1000)
            data = data.decode()
            print('接收到信息:' + data)
            try:
                if data == 'stop':
                    self.run_flag = False
                    print('已关闭录像！')
                elif data == 'open':
                    try:
                        self.init_camera()
                    except:
                        print("摄像头初始化失败")
                    thread_cam = _thread.start_new_thread(self.start_capture, ())
                    self.run_flag = True
                else:
                    command = eval(data)   # 命令形如:['up', 30, 10]
                    direction = command[0]
                    angle = command[1]
                    speed = command[2]
                    if direction == 'up':
                        sg90.up(angle, speed)
                    elif direction == 'down':
                        sg90.down(angle, speed)
                    elif direction == 'left':
                        sg90.left(angle, speed)
                    elif direction == 'right':
                        sg90.right(angle, speed)

            except:
                print('错误！！！请重连')

    def start_capture(self):
        print("摄像线程开始运行")
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        try:
            while self.run_flag:
                buf = camera.capture()  # 获取图像数据
                udp_sock.sendto(buf, self.addr)  # 向服务器发送图像数据
                # time.sleep(2)
                print("发送...done")
        except:
            print("发送...结束")
        finally:
            self.run_flag = False
            udp_sock.close()
            print("摄像线程结束运行")
            camera.deinit()

    def stop_capture(self):
        self.run_flag = False
        camera.deinit()


if __name__ == '__main__':
    cam = Cam()
    cam.loop()








