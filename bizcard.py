#!/usr/bin/env python
# coding=utf-8

import cv2
import numpy as np

import util
import lqs2


class BizCardDetector(object):

    def __init__(self):

        """scale for resize input image"""
        self.scale = 1.

    def zoom_out_image(self, img):

        small_resolution = 640 * 480
        self.scale = np.sqrt(img.shape[1]*img.shape[0]*1.0 / small_resolution)
        print (int(img.shape[1] / self.scale), int(img.shape[0] / self.scale))
        return cv2.resize(img, (int(img.shape[1] / self.scale), int(img.shape[0] / self.scale)))

    def detect_card(self, img):

        small = self.zoom_out_image(img)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)

        contours = util.find_top_k_contours(edges, 3)
        contours_img = edges.copy()
        contours_img[...] = 0
        cv2.drawContours(contours_img, contours, -1, (255, 255, 255), 1)

        lines = cv2.HoughLines(contours_img, 1, np.pi / 180, 100)
        if lines is None:
            return None
        reduced_v_lines, reduced_h_lines = util.reduce_lines(lines[0])

        quad_on_small = lqs2.largest_quadrangle_search(reduced_v_lines, reduced_h_lines, small.shape[1], small.shape[0])

        if quad_on_small:
            #util.draw_quadrangle(small, quad_on_small)
            #cv2.imshow('quadrangle', small)
            #cv2.waitKey(0)
            return [[int(p[0]*self.scale), int(p[1]*self.scale)] for p in quad_on_small] #quad on input img

        return None

if __name__ == '__main__':

    input_img_path = '/Users/kevinhuang/PycharmProjects/cardDetect2/res/jiandongCard/IMG_4080.JPG'
    detector = BizCardDetector()
    img = cv2.imread(input_img_path)
    quad = detector.detect_card(img)
    if quad:
        util.draw_quadrangle(img, quad)
        small = cv2.resize(img, (int(img.shape[1] / detector.scale), int(img.shape[0] / detector.scale)))
        cv2.imshow('quadrangle', small)
        cv2.waitKey(0)
    else:
        print "no bizcard detected!"
