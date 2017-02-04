#!/usr/bin/env python
# coding=utf-8

import cv2
import numpy as np

import util
import lqs2


class BizCardDetector(object):

    def __init__(self, scale=6):

        """scale for resize input image"""
        self.scale = scale

    def detect_card(self, img):

        small = cv2.resize(img, (int(img.shape[1] / self.scale), int(img.shape[0] / self.scale)))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        contours = util.find_top_k_contours(edges, 3)
        contours_img = edges.copy()
        contours_img[...] = 0
        cv2.drawContours(contours_img, contours, -1, (255, 255, 255), 1)

        lines = cv2.HoughLines(contours_img, 1, np.pi / 180, 100)
        reduced_v_lines, reduced_h_lines = util.reduce_lines(lines[0])

        quad_on_small = lqs2.largest_quadrangle_search(reduced_v_lines, reduced_h_lines, small.shape[1], small.shape[0])

        if quad_on_small:
            #util.draw_quadrangle(small, quad_on_small)
            #cv2.imshow('quadrangle', small)
            #cv2.waitKey(0)
            return [[p[0]*self.scale, p[1]*self.scale] for p in quad_on_small] #quad on input img

        return None

if __name__ == '__main__':
    pass
