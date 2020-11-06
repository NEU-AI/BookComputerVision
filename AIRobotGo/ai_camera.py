#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2
import numpy as np
import ai_findchessboard as fc
from logger import logger

LINESNUM = 9


class Camera(object):
    def __init__(self,logger):
        self.chessstate = []
        self.chessarray = []
        self.finalchessarray = []
        self.crossarray = []
        self.capture = cv2.VideoCapture(0)
        self.update_chessboard()

    # 开始判断人下的棋子
    def getcapture(self):
        ret, frame = self.capture.read()
        cv2.imshow("capture",frame)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            return None
        #logger.info("get capture frame")
        return frame

    # 开始识别棋盘
    def update_chessboard(self):

        while True:
            frame = self.getcapture()
            if frame is None:
                break
            self.crossarray = fc.checklines(self.chessboardedges(frame), frame.shape)
            if self.crossarray is not None:
                break
        if self.crossarray is not None:
            self.chessstate = [[0 for i in range(len(self.crossarray[0]))] for i in range(len(self.crossarray))]
        else:
            print ("can not find board")

    def chessboardedges(self, image):
        blur = cv2.medianBlur(image, 3)

        # 彩色图片灰度化
        gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

        ret, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        # cv2.imshow("thresh1", thresh1)

        kernel = np.ones((3, 3), np.uint8)
        edged = cv2.dilate(thresh1, kernel)
        # cv2.imshow("dilate", edged)
        edged = cv2.erode(edged, kernel)
        cv2.imshow("erode", edged)

        # 执行边缘检测
        edges = cv2.Canny(edged, 50, 120)
        cv2.imshow('Edges', edges)

        return edges

    def findchess(self):

        image = self.getcapture()
        if image is None:
            return False,None
        cross = self.crossarray
        cv2.imshow('image', image)

        global crossArr
        crossArr = cross
        # blur = cv2.medianBlur(image, 3)

        # 彩色图片灰度化
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #cv2.imshow('gray', gray)

        gray = cv2.medianBlur(gray, 5)

        ret, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        #cv2.imshow('threshold', threshold)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                   param1=50, param2=30, minRadius=0, maxRadius=60)

        isfind = False
        newitem = []
        # 确保至少发现一个圆
        if circles is not None:
            # 进行取整操作
            circles = np.int0(np.around(circles))
            # 循环遍历所有的坐标和半径
            for i in circles[0, :]:
                # print((i[0], i[1]), threshold[i[1], i[0]])
                if threshold[i[1], i[0]] == 255:
                    continue
                cv2.circle(image, (i[0], i[1]), i[2], (0, 0, 255), 2)  # 画出外圆
                cv2.circle(image, (i[0], i[1]), 2, (0, 0, 255), 3)  # 画出圆心
                isfind, item = self.modifyaxis(i[0], i[1], threshold[i[1], i[0]])
                if isfind:
                    newitem = item
                    break
            cv2.imshow('image', image)
        return isfind, newitem

    # 矫正棋子圆心坐标为交点
    def modifyaxis(self, xaxis, yaxis, value):
        item = []
        isfound = False
        if value == 255:
            value = -1
        else:
            value = 1

        # print(len(crossArr))
        if len(crossArr) != LINESNUM:
            print ("cross error")
            return isfound, item
        countx = len(crossArr)
        county = len(crossArr[0])
        index_xaxis = []
        index_yaxis = []

        isfound = False

        for y_index in range(0, county):
            value_y = crossArr[0][y_index][0]
            if abs(xaxis - value_y) < 15:
                index_yaxis.append(y_index)
                isfound = True
                break

        if not isfound:
            return isfound, item

        isfound = False
        for x_index in range(0, countx):
            value_x = crossArr[x_index][0][1]
            if abs(yaxis - value_x) < 15:
                index_xaxis.append(x_index)
                isfound = True
                break

        if not isfound:
            return isfound, item

        isfound = False
        # 判断当前是否存在这个棋子
        isfound = self.checknewitem([index_xaxis[0], index_yaxis[0]], self.chessarray)

        if not isfound:
            #self.chessarray.append([index_xaxis[0], index_yaxis[0]])
            item = [index_xaxis[0], index_yaxis[0]]
            isfound = True
            print("state_cur", self.chessarray)
        else:
            isfound = False

        return isfound, item

    def checknewitem(self, item, cur_array):
        isfound = False
        if item in cur_array:
            isfound = True
        return isfound

    def appendnewitem(self,item):
        self.chessarray.append(item)
        self.chessstate[item[0]][item[1]] = 1