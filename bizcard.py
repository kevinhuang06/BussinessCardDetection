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
        self.scale = np.sqrt(img.shape[1] * img.shape[0] * 1.0 / small_resolution)
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
            # util.draw_quadrangle(small, quad_on_small)
            # cv2.imshow('quadrangle', small)
            # cv2.waitKey(0)
            return [[int(p[0] * self.scale), int(p[1] * self.scale)] for p in quad_on_small]  # quad on input img

        return None

    def rectangle_card(self, img, quad):

        len_left_edge = int(np.linalg.norm([quad[1][0] - quad[0][0], quad[1][1] - quad[0][1]]))
        len_right_edge = int(np.linalg.norm([quad[3][0] - quad[2][0], quad[3][1] - quad[2][1]]))
        width = max(len_left_edge, len_right_edge)
        len_top_edge = int(np.linalg.norm([quad[2][0] - quad[1][0], quad[2][1] - quad[1][1]]))
        len_bottom_edge = int(np.linalg.norm([quad[0][0] - quad[3][0], quad[0][1] - quad[3][1]]))
        height = max(len_top_edge, len_bottom_edge)
        print quad
        src = np.float32([quad[0], quad[1], quad[3], quad[2]])
        dst = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

        matrix = cv2.getPerspectiveTransform(src, dst)
        return cv2.warpPerspective(img, matrix, (width, height))


def sample_detect(input_img_path='/Users/kevinhuang/PycharmProjects/cardDetect2/res/jiandongCard/IMG_4082.JPG'):
    # input_img_path = '/Users/kevinhuang/PycharmProjects/cardDetect2/res/jiandongCard/IMG_4082.JPG'
    detector = BizCardDetector()
    img = cv2.imread(input_img_path)
    quad = detector.detect_card(img)
    if quad:
        #util.draw_quadrangle(img, quad)
        small = cv2.resize(img, (int(img.shape[1] / detector.scale), int(img.shape[0] / detector.scale)))
        # cv2.imshow('quadrangle', small)
        # cv2.waitKey(0)
        rect_card = detector.rectangle_card(img, quad)
        card_resolution = 854*480
        card_scale = np.sqrt(rect_card.shape[1]*rect_card.shape[0]*1./card_resolution)
        small_rect_card = cv2.resize(rect_card,
                                     (int(rect_card.shape[1] / card_scale),
                                      int(rect_card.shape[0] / card_scale)))

        #cv2.imshow('quadrangle', small_rect_card)
        #cv2.waitKey(0)
        return small_rect_card

    else:
        print "no bizcard detected!"
        return None


if __name__ == '__main__':
    sample_detect()
