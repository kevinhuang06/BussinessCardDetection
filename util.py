# coding=utf-8

import cv2
import numpy as np


def find_top_k_contours(edges, k):
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours_with_len = []
    for con in contours:
        contours_with_len.append([con, len(con)])
    sorted_contours = sorted(contours_with_len, key=lambda x: x[1], reverse=True)
    k = min(k, len(sorted_contours))

    return [sorted_contours[i][0] for i in range(k)]


def similar_line(l1, l2):
    return abs(l1[0] - l2[0]) < 10 and abs(l1[1] - l2[1]) < 5 * np.pi / 180


def merge_similar_lines(lines):
    merged_lines = []
    sorted_lines = sorted(lines, key=lambda x: (abs(x[0]), x[1]))

    if sorted_lines:
        last = sorted_lines[0]
        for i in range(1, len(sorted_lines)):
            curr = sorted_lines[i]
            if similar_line(curr, last):
                last = [(last[0] + curr[0]) / 2., (last[1] + curr[1]) / 2.]
            else:
                merged_lines.append(last)
                last = curr
        merged_lines.append(last)

    return merged_lines


def remove_lines_not_perpendicular_to_any_line(v_lines, h_lines):

    min_rad = 80 * np.pi / 180.0
    max_rad = 100 * np.pi / 180.0
    v_lines_collect = []
    h_lines_collect = []

    for vl in v_lines:
        for hl in h_lines:
            if min_rad < abs(vl[1] - hl[1]) < max_rad:
                v_lines_collect.append(vl)
                break

    for hl in h_lines:
        for vl in v_lines_collect:
            if min_rad < abs(vl[1] - hl[1]) < max_rad:
                h_lines_collect.append(hl)
                break

    return v_lines_collect, h_lines_collect


def reduce_lines(lines):

    h_lines = []
    v_lines = []
    for line in lines:
        theta = line[1]
        if (theta < (np.pi / 4.)) or (theta > (3. * np.pi / 4.0)):
            h_lines.append(line)
        else:
            v_lines.append(line)

    return remove_lines_not_perpendicular_to_any_line(
                merge_similar_lines(v_lines), merge_similar_lines(h_lines))


def draw_quadrangle(img, quad):

    cv2.line(img, (quad[0][0], quad[0][1]), (quad[1][0], quad[1][1]), (255, 0, 0), 3)
    cv2.line(img, (quad[1][0], quad[1][1]), (quad[2][0], quad[2][1]), (255, 0, 0), 3)
    cv2.line(img, (quad[2][0], quad[2][1]), (quad[3][0], quad[3][1]), (255, 0, 0), 3)
    cv2.line(img, (quad[3][0], quad[3][1]), (quad[0][0], quad[0][1]), (255, 0, 0), 3)
