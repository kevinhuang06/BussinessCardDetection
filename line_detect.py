# coding=utf-8
import cv2
import glob
import os
import sys
import time
import numpy as np
from lQS import *

def draw_vertical_line(line, small):
    rho = line[0]  # 第一个元素是距离rho
    theta = line[1]  # 第二个元素是角度theta
    pt1 = (int(rho / np.cos(theta)), 0)
    # 该直线与最后一行的焦点
    pt2 = (int((rho - small.shape[0] * np.sin(theta)) / np.cos(theta)), small.shape[0])
    # 绘制一条红线
    cv2.line(small, pt1, pt2, (0, 0, 255))


def draw_horizontal_line(line, small):
    rho = line[0]  # 第一个元素是距离rho
    theta = line[1]  # 第二个元素是角度theta
    pt1 = (0, int(rho / np.sin(theta)))
    # 该直线与最后一列的交点
    pt2 = (small.shape[1], int((rho - small.shape[1] * np.cos(theta)) / np.sin(theta)))
    # 绘制一条直线
    cv2.line(small, pt1, pt2, (0, 0, 255), 1)


def drawLines(lines, img):
    for i, l in enumerate(lines):
        cv2.line(img, (l[0], l[1]), (l[2], l[3]), (0,0,255), 1)
        # cv2.imshow('lines', img)
        # cv2.waitKey(0)
        # print img.shape
        # print lines
        # pass


img_inputpath = []
canny_outputpath = []


def similar_line(l1, l2):
    # 10 pix for rho, 4.87 du for theta
    # print abs(l1[0]-l2[0]) < 10, abs(l1[1]-l2[1]) < 0.085
    if abs(l1[0] - l2[0]) < 10 and abs(l1[1] - l2[1]) < 0.085:  # ~4.87/180
        return True
    else:
        return False


def merge_similar_lines(lines):
    merged_lines = []
    sorted_lines = sorted(lines, key=lambda x: (x[0], x[1]))
    # sorted_lines = sorted(sorted_lines, key=lambda x: x[1])
    if len(sorted_lines) == 0:
        return []
    last = sorted_lines[0]  # may be no line
    for i in range(1, len(sorted_lines)):
        curr = sorted_lines[i]
        if similar_line(curr, last):
            last = [(last[0] + curr[0]) / 2., (last[1] + curr[1]) / 2.]
        else:
            merged_lines.append(last)
            last = curr
    merged_lines.append(last)
    return merged_lines


def remove_lines_has_no_vertical_pair(v_lines, h_lines):
    min_rad = 80 * np.pi / 180.0
    max_rad = 100 * np.pi / 180.0
    # remove v
    v_lines_collect = []
    h_lines_collect = []
    for vl in v_lines:
        flag = False
        for hl in h_lines:
            if min_rad < abs(vl[1] - hl[1]) < max_rad:
                flag = True
        if flag:
            v_lines_collect.append(vl)

    # remove h
    for hl in h_lines:
        flag = False
        for vl in v_lines_collect:
            if min_rad < abs(vl[1] - hl[1]) < max_rad:
                flag = True
        if flag:
            h_lines_collect.append(hl)
    return v_lines_collect, h_lines_collect


def houghSpace_to_cartesian_v4(theta, rho):
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + 1000 * (-b))
    y1 = int(y0 + 1000 * a)
    x2 = int(x0 - 1000 * (-b))
    y2 = int(y0 - 1000 * a)
    return [x1, y1, x2, y2]


def draw_quadrangle(Q, img):
    cv2.line(img, (Q[0].x, Q[0].y), (Q[1].x, Q[1].y), (255, 0, 0), 3)
    cv2.line(img, (Q[1].x, Q[1].y), (Q[2].x, Q[2].y), (255, 0, 0), 3)
    cv2.line(img, (Q[2].x, Q[2].y), (Q[3].x, Q[3].y), (255, 0, 0), 3)
    cv2.line(img, (Q[3].x, Q[3].y), (Q[0].x, Q[0].y), (255, 0, 0), 3)

def lineCard():
    cc = 0
    for ipath in glob.glob("/Users/kevinhuang/PycharmProjects/cardDetect2/jiandongCard/*.JPG"):
        # print ipath
        bname = os.path.basename(ipath)
        _outputpath = os.path.join("/Users/kevinhuang/PycharmProjects/cardDetect2/box_jiandongCard/",
                                   bname)

        img = cv2.imread(ipath)

        start = time.time()
        small = cv2.resize(img, (int(img.shape[1] / 6), int(img.shape[0] / 6)))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        len_contours = []
        filter_contours = []
        for con in contours:
            if len(con) > 100:
                len_contours.append([len(con), con])
                filter_contours.append(con)
        sorted_contours = sorted(len_contours, key=lambda x: x[0], reverse=True)
        top_contours = []
        for i in range(3):
            top_contours.append(sorted_contours[i][1])

        bu_img = edges.copy()
        bu_img[...] = 0
        cv2.drawContours(bu_img, top_contours, -1, (255, 255, 255), 1)
        lines = cv2.HoughLines(bu_img, 1, np.pi / 180, 100)  # 这里对最后一个参数使用了经验型的值
        result = gray.copy()

        sorted_horizontal_lines = []
        sorted_vertical_lines = []
        for line in lines[0]:
            rho = line[0]  # 第一个元素是距离rho
            theta = line[1]  # 第二个元素是角度theta
            # print rho
            # print theta

            if (theta < (np.pi / 4.)) or (theta > (3. * np.pi / 4.0)):  # 垂直直线
                # 该直线与第一行的交点
                # draw_vertical_line(line,small)
                sorted_vertical_lines.append(line)
            else:  # 水平直线
                # draw_horizontal_line(line,small)
                sorted_horizontal_lines.append(line)
        if 'IMG_4025' in _outputpath:
            pass
        merged_vertical_lines = merge_similar_lines(sorted_vertical_lines)
        merged_horizontal_lines = merge_similar_lines(sorted_horizontal_lines)

        filtered_v_lines, filtered_h_lines = remove_lines_has_no_vertical_pair(merged_vertical_lines,
                                                                               merged_horizontal_lines)

        for l in filtered_v_lines:
            draw_vertical_line(l, small)

        for l in filtered_h_lines:
            draw_horizontal_line(l, small)
        num_h, num_v = len(merged_horizontal_lines), len(merged_vertical_lines)
        num_filter_h, num_filter_v = len(filtered_h_lines), len(filtered_v_lines)
        reduce = len(lines[0]) - num_h - num_v

        bestQ,area = largest_quadrangle_search(filtered_h_lines, filtered_v_lines, small)

        #print_q(bestQ)
        #print 'max_area :%s' % area
        if bestQ:
            cc += 1
            draw_quadrangle(bestQ, small)
        # cv2.imshow('Canny', bu_img)
        # cv2.waitKey(0)
        # cv2.imshow('Result', result)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        # sys.exit(0)
        end = time.time()
        during = end - start
        print "num lines:%s，merged_lines:%s,filtered:%s,len_reduce:%s, detect time:%s bname:%s" \
              % (len(lines[0]), (num_h, num_v), (num_filter_h, num_filter_v), reduce, during, bname)
        cv2.imwrite(_outputpath, small)
    print cc