#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cv2

LINESNUM = 9
MAXPERPIXEL = 50
MINPERPIXEL = 25


def sortedlines(lines, pos):
    count = len(lines)

    for i in range(count):  # type: int
        for j in range(0, count - i - 1):
            if lines[j][pos] > lines[j + 1][pos]:
                lines[j], lines[j + 1] = lines[j + 1], lines[j]

    return lines


# 去除相邻过近的边
def deletelines(lines, pos):
    newline = []
    count = len(lines)
    index = 0
    loop = 3
    # 如果相邻两个边距离很近，就保留前一个边，抛弃相邻的边。有可能识别出连续的相邻很近的边，所以轮询3遍
    while index <= count - 1:
        newline.append(lines[index])
        if lines[index + 1][pos] - lines[index][pos] <= MINPERPIXEL:
            index += 2
        else:
            index += 1
        if index + 1 == count:  # 如果是前一条边是倒数第2条边或第3条边的情况不会漏掉最后一条边
            newline.append(lines[index])
        if index + 1 >= count:
            if loop > 0:
                index = 0
                loop -= 1
                lines = newline[:]  # copy.deepcopy(newline)
                newline = []
                count = len(lines)
            else:
                break
    return lines


def showimage(title, shape, linesx, linesy):
    countx = len(linesx)
    image_result1 = np.ones(shape)

    for i in range(0, countx):
        x1, y1, x2, y2 = linesx[i]
        cv2.line(image_result1, (x1, y1), (x2, y2), (255, 0, 255), 1)

    county = len(linesy)
    for i in range(0, county):
        x1, y1, x2, y2 = linesy[i]
        cv2.line(image_result1, (x1, y1), (x2, y2), (255, 0, 255), 1)

    cv2.imshow(title, image_result1)


def checklines(edges, shape):
    crossArr = []
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 1, minLineLength=60, maxLineGap=10)

    linesx = []
    linesy = []

    if lines is None:
        return

    # 提取出行和列
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 - x1 <= 3:
            line[0][2] = line[0][0]
            linesy.append(line[0])
        elif y2 - y1 <= 3:
            line[0][3] = line[0][1]
            linesx.append(line[0])

    # print("X:", linesx)
    # print("Y:", linesy)
    #showimage("edgeds", shape, linesx, linesy)

    # 定义好是几个格子的棋盘15*15
    if len(linesx) < LINESNUM:
        # print("is not chessboard")
        return
    if len(linesy) < LINESNUM:
        # print("is not chessboard")
        return

    # 行和列进行排序
    countx = len(linesx)
    linesx = sortedlines(linesx, 1)

    firstypos = linesx[0][1]
    finalypos = linesx[countx - 1][1]

    # print(firstypos,finalypos)

    county = len(linesy)
    linesy = sortedlines(linesy, 0)

    firstxpos = linesy[0][0]
    finalxpos = linesy[county - 1][0]
    # print(firstxpos,finalxpos)
    #
    # print("sorted X:",linesx)
    # print("sorted Y:",linesy)

    # 去除相邻过近的行和列线
    newlinex = deletelines(linesx, 1)
    newliney = deletelines(linesy, 0)

    countx = len(newlinex)
    county = len(newliney)

    if countx < LINESNUM:
        # print ("is not board")
        # reset()
        return
    if county < LINESNUM:
        # print ("is not board")
        # reset()
        return
    if countx != county:
        return

    # 根据长度和宽度，延长过短的线段
    countx = len(newlinex)
    for i in range(0, countx):
        x1, y1, x2, y2 = newlinex[i]
        newlinex[i][0] = firstxpos
        newlinex[i][2] = finalxpos

    county = len(newliney)
    for i in range(0, county):
        x1, y1, x2, y2 = newliney[i]
        newliney[i][1] = firstypos
        newliney[i][3] = finalypos

    # 计算每个线的交点
    for i in range(0, countx):
        temparr = []
        for j in range(0, county):
            temparr.append((newliney[j][0], newlinex[i][1]))
        crossArr.append(temparr)

    print("newx", newlinex)
    print("newy", newliney)

    county = len(newliney)
    print("cross", crossArr)

    # 根据行的最后一个坐标和列的最后一个坐标，确定行和列的终点
    finalxpos = crossArr[0][county - 1][0]
    finalypos = crossArr[countx - 1][0][1]

    # 更新把最后行交点和最后一列的交点做为棋盘的终线
    countx = len(newlinex)
    for i in range(0, countx):
        x1, y1, x2, y2 = newlinex[i]
        # if( abs(x1 -x2) < finalXPos - firstXPos):
        newlinex[i][0] = firstxpos
        newlinex[i][2] = finalxpos

    county = len(newliney)
    for i in range(0, county):
        x1, y1, x2, y2 = newliney[i]
        # if( abs(y1 -y2) < finalYPos - firstYPos):
        newliney[i][1] = firstypos
        newliney[i][3] = finalypos

    #showimage("board", shape, newlinex, newliney)

    return crossArr
