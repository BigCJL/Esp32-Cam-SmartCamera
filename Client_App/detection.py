# -*- coding: utf-8 -*-
# @Time     : 2023-03-12 13:10
# @Author   : Big Cheng
# @FileName : detection.py
import cv2
configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'
classFile = 'coco.names'

class detector:
    def __init__(self, thres = 0.6):
        self.thres = thres
        self.net = cv2.dnn_DetectionModel(weightsPath, configPath)
        self.net.setInputSize(320, 320)
        self.net.setInputScale(1.0 / 127.5)
        self.net.setInputMean((127.5, 127.5, 127.5))
        self.net.setInputSwapRB(True)
        self.classNames = []
        with open(classFile, 'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')

    def detect(self, img, target='person'):
        classIds, confs, bbox = self.net.detect(img, confThreshold=self.thres)
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv2.putText(img, self.classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, str(round(confidence * 100, 2)), (box[0] + 200, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        return img

    def auto_trace(self, img, target='person'):
        command = ''
        classIds, confs, bbox = self.net.detect(img, confThreshold=self.thres)
        if len(classIds) != 0:
            for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
                if target != self.classNames[classId - 1]:
                    continue
                center_target = (int((box[0] + box[2] / 2)), int((box[1] + box[3] / 2)))
                center = (int(img.shape[1] / 2), int(img.shape[0] / 2))
                cv2.circle(img, center_target, 10, (0, 0, 255), -1)
                cv2.circle(img, center, 10, (0, 0, 255), -1)
                horizon = center_target[0] - center[0]
                vertical = center_target[1] - center[1]

                if horizon > 100:   # 目标在屏幕右侧
                    command = "right"
                elif horizon < -100:
                    command = 'left'
                if vertical > 100:  # 目标在屏幕下侧
                    command = 'down'
                elif vertical < -100:
                    command = 'up'
                cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                cv2.putText(img, self.classNames[classId - 1].upper(), (box[0] + 10, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(img, str(round(confidence * 100, 2)) + "追踪中", (box[0] + 200, box[1] + 30),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        return img, command

if __name__ == '__main__':
    det = detector()
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3, 1280)
    cap.set(4, 720)
    cap.set(10, 70)
    while True:
        success, img = cap.read()
        img = det.auto_trace(img)
        cv2.imshow("Output", img)
        cv2.waitKey(1)