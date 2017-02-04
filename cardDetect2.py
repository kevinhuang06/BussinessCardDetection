import cv2
import time
import numpy as np
#from canny_card import *
#from find_card import *
import sys
from line_detect import *
from largestQuadrangleSearch import *
from bizcard import  BizCardDetector
import util

def distance_point_line():
    pass
def drawLines(lines,img, _outputpath):
    for i,l in enumerate(lines):
        cv2.line(img, (l[0],l[1]),(l[2],l[3]),10*i+100,1)
    cv2.imwrite(_outputpath, img)
    #cv2.imshow('lines', img)
    #cv2.waitKey(0)
    #print img.shape
   # print lines
    #pass


def new_detect():
    detector = BizCardDetector()
    cc = 0
    for ipath in glob.glob("/Users/kevinhuang/PycharmProjects/cardDetect2/res/jiandongCard/*.JPG"):

        bname = os.path.basename(ipath)
        _outputpath = os.path.join("/Users/kevinhuang/PycharmProjects/cardDetect2/res/box_stanford_big/", bname)

        #print ipath
        img = cv2.imread(ipath)

        quad = detector.detect_card(img)
        if quad:
            cc += 1
            util.draw_quadrangle(img, quad)
        else:
            print bname
        cv2.imwrite(_outputpath, img)
    print cc


def main():
    lineCard()
    #new_detect()
    sys.exit(0)
    cc = 0
    for ipath in glob.glob("/Users/kevinhuang/PycharmProjects/cardDetect2/jiandongCard/*.JPG"):
        print ipath
        bname = os.path.basename(ipath)
        _outputpath = os.path.join("/Users/kevinhuang/PycharmProjects/cardDetect2/line_jiandongCard/", bname)
        img = cv2.imread(ipath)
        small = cv2.resize(img, (int(img.shape[1] / 6), int(img.shape[0] / 6)))
        print small.shape
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        #gray = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
        #cv2.imshow('gray', gray)
        #cv2.waitKey(0)
        img_bw = cv2.Canny(gray, 50, 150)
        contours, hierarchy = cv2.findContours(img_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        len_contours = []
        filter_contours = []
        for con in contours:
            if len(con)>100:
                len_contours.append([len(con),con])
                filter_contours.append(con)
        sorted_contours = sorted(len_contours, key=lambda x:x[0],reverse=True)
        top_contours = []
        for i in range(3):
            top_contours.append(sorted_contours[i][1])

        bu_img = img_bw.copy()
        bu_img[...] = 0
        cv2.drawContours(bu_img, top_contours, -1, (255, 255, 255), 1)
        #cv2.imwrite(_outputpath, bu_img)
        #cv2.imshow('contours',bu_img)
        #cv2.waitKey(2000)
        #print contours[0]
        lines = cv2.HoughLinesP(bu_img, 1, np.pi / 180, 30, 60, 10);
        black_img = img_bw.copy()
        black_img[...] = 0
        slope_off_lines = []
        horizonLines = []
        slope_horizon = []
        verticalLines = []
        slope_vertical = []
        for l in lines[0]:
            A,B,C = line([l[0],l[1]],[l[2],l[3]])
            slope_off_lines.append([round(A*1.0/B,2), 1, round(C*1.0/B,2)])
            if round(A*1.0/B,2) > 0:
                horizonLines.append(l)
                slope_horizon.append([round(A*1.0/B,2),round(C*1.0/B,2),round(distance([l[0],l[1]],[l[2],l[3]]),0)])
            else:
                verticalLines.append(l)
                slope_vertical.append([round(A*1.0/B,2),round(C*1.0/B,2),round(distance([l[0],l[1]],[l[2],l[3]]),0)])
        slope_horizon.sort(key=lambda x:x[1])
        slope_vertical.sort(key=lambda x:x[1])
        drawLines(horizonLines, black_img, _outputpath)
        #black_img[...] = 0
        drawLines(verticalLines, black_img, _outputpath)
        #sys.exit(0)
        quad = None#largestQuadrangleSearch(lines[0], black_img)

        if quad != None:
            black_img = gray.copy()
            black_img[...] = 0
            cv2.line(small, (quad[0][0], quad[0][1]), (quad[1][0], quad[1][1]),  (0,0,255), 1)
            cv2.line(small, (quad[1][0], quad[1][1]), (quad[2][0], quad[2][1]), (0,0,255), 1)
            cv2.line(small, (quad[2][0], quad[2][1]), (quad[3][0], quad[3][1]), (0,0,255), 1)
            cv2.line(small, (quad[3][0], quad[3][1]), (quad[0][0], quad[0][1]), (0,0,255), 1)
            #cv2.imshow('gray2', small)
            #cv2.waitKey(2000)
            cv2.imwrite(_outputpath,small)
            print "quad: %s" %quad
            cc += 1
        else:
            #cv2.imwrite(_outputpath, bu_img)
            print "No Quadrangle Detected!"
        #sys.exit(0)
    print '%s card detect'%cc
if __name__ == '__main__':
    main()