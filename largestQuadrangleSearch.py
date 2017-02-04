import cv2
import glob
import os
import numpy as np

from find_card import *


def checkBoundaray4Point(point, icols, irows):
    if point[0] < 0 or point[0] >= icols or point[1] < 0 or point[1] >= irows:
        return False
    return True
def quadArea(p0,p1,p2,p3):

    x1 = p2[0] - p0[0]
    y1 = p2[1] - p0[1]
    x2 = p3[0] - p1[0]
    y2 = p3[1] - p1[1]
    return abs(x1*y2 - x2*y1)/2;

def AngleBetween2Vecs(va,vb):

    interPtoduct = va[0] * vb[0] + va[1] * vb[1];
    vaModule = np.linalg.norm(va)
    vbModule = np.linalg.norm(vb)
    cos_ab = interPtoduct / (vbModule * vaModule);
    return np.arccos(cos_ab)*180/np.pi;


def checkAngle(p0,p1,p2,p3):
    angles = []
    vec_ad = [p3[0] - p0[0], p3[1] - p0[1]]
    vec_ab = [p1[0] - p0[0], p1[1] - p0[1]]
    angles.append(AngleBetween2Vecs(vec_ad,vec_ab))

    vec_ba = [p0[0] - p1[0], p0[1] - p1[1]]
    vec_bc = [p2[0] - p1[0], p2[1] - p1[1]]
    angles.append(AngleBetween2Vecs(vec_ba,vec_bc))

    vec_cb = [p1[0] - p2[0], p1[1] - p2[1]]
    vec_cd = [p3[0] - p2[0], p3[1] - p2[1]]
    angles.append(AngleBetween2Vecs(vec_cb,vec_cd))

    vec_dc = [p2[0] - p3[0], p2[1] - p3[1]]
    vec_da = [p0[0] - p3[0], p0[1] - p3[1]]
    angles.append(AngleBetween2Vecs(vec_dc, vec_da))

    for a in angles:
        if a < 80 or a > 100:
            return False
    return True


def checkAspectRatio(p0,p1,p2,p3):
    normL = []
    normL.append(np.linalg.norm([p1[0] - p0[0], p1[1] - p0[1]]))
    normL.append(np.linalg.norm([p2[0] - p1[0], p2[1] - p1[1]]))
    normL.append(np.linalg.norm([p3[0] - p2[0], p3[1] - p2[1]]))
    normL.append(np.linalg.norm([p0[0] - p3[0], p0[1] - p3[1]]))
    aspect = np.min(normL)/ np.max(normL)
    print "aspect:%s" % aspect
    if aspect < 0.5 or aspect > 0.75:
        return False
    else:
        return True

def avgOfPointLoc(points):
    sumX = 0
    sumY = 0
    for p in points:
        sumX += p[0]
        sumY += p[1]
    if len(points) > 0:
        return sumX/len(points),sumY/len(points)
    return 0,0
def quadPoint4Part(pointSeq):
    avg_x, avg_y = avgOfPointLoc(pointSeq)
    pointBlock = [[],[],[],[]]
    for p in pointSeq:
        if p[1] < avg_y:
            if p[0] < avg_x:
                pointBlock[0].append(p)  #topLeft
            else:
                pointBlock[1].append(p)  #topRight
        else:
            if p[0] >= avg_x:
                pointBlock[2].append(p)  # DownRight
            else:
                pointBlock[3].append(p)  # DownRight
    return pointBlock

def largestQuadrangleSearch(lines, img):
    crossPoint = []
    slope ={}
    for i in range(len(lines)):
        for  j in range(len(lines)):
            L1 = line(lines[i][:2], lines[i][2:])
            L2 = line(lines[j][:2], lines[j][2:])
            loc = intersection(L1,L2)
            if loc != False:
                # check bound
                if checkBoundaray4Point(loc, img.shape[1], img.shape[0]):
                    crossPoint.append(loc)


    pointBlocks = quadPoint4Part(crossPoint)
    filtereBlocks = []
    for pb in pointBlocks:
        filtereBlocks.append(set(pb))
    uLeftOrder = sorted(filtereBlocks[0], key=uLeftSort)
    uRightOrder = sorted(filtereBlocks[1], key=uRightSort, reverse=True)
    lRightOrder = sorted(filtereBlocks[2], key=lRightSort,reverse=True)
    lLeftOrder = sorted(filtereBlocks[3], key=lLeftSort,reverse=True)

    uLeft = uLeftOrder[0:4]
    uRight = uRightOrder[0:4]
    lLeft = lLeftOrder[0:4]
    lRight = lRightOrder[0:4]
    # calc area
    areaThres = img.shape[0]*img.shape[1]/4
    max_area = areaThres# area thres:  1/3 * area(img)
    bestQ = None
    for idx,p0 in enumerate(uLeft):
        #print "idx:%s" %idx
        for id1,p1 in enumerate(uRight):
            #print "p1:%s" %id1
            for p2 in lRight:
                for p3 in lLeft:
                    area = quadArea(p0, p1, p2, p3)
                    if area > max_area:
                        if checkAngle(p0, p1, p2, p3) and checkAspectRatio(p0, p1, p2, p3):
                            max_area = area
                            bestQ = [p0,p1,p2,p3]
    #print "maxArea:%s"%max_area
    if max_area > areaThres:
        return bestQ
    else:
        return None

