import cv2
import glob
import os
import numpy as np

from find_card import *
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y



def checkByBoundarayCondition(Q, cols, rows):
    for p in Q:
        if p.x < 0 or p.x > cols or p.y < 0 or p.y > rows:
            return False
    return True


def quadArea(Q):

    x1 = Q[2].x - Q[0].x
    y1 = Q[2].y - Q[0].y
    x2 = Q[3].x - Q[1].x
    y2 = Q[3].y - Q[1].y
    return abs(x1*y2 - x2*y1)/2

def AngleBetween2Vecs(va,vb):

    inter_product = va.x * vb.x + va.y * vb.y

    va_module = np.sqrt(np.power(va.x, 2) + np.power(va.y, 2))
    vb_module = np.sqrt(np.power(vb.x, 2) + np.power(vb.y, 2))
    cos_ab = inter_product / (vb_module * va_module)
    return np.arccos(cos_ab)*180/np.pi


def check_angle(Q):
    angles = []
    #dab
    vec_ad = Point(Q[3].x-Q[0].x, Q[3].y-Q[0].y)
    vec_ab = Point(Q[1].x-Q[0].x, Q[1].y-Q[0].y)
    angles.append(AngleBetween2Vecs(vec_ad, vec_ab))
    #abc
    vec_ba = Point(Q[0].x-Q[1].x, Q[0].y-Q[1].y)
    vec_bc = Point(Q[2].x-Q[1].x, Q[2].y-Q[1].y)
    angles.append(AngleBetween2Vecs(vec_ba, vec_bc))
    #bcd
    vec_cb = Point(Q[1].x-Q[2].x, Q[1].y-Q[2].y)
    vec_cd = Point(Q[3].x-Q[2].x, Q[3].y-Q[2].y)
    angles.append(AngleBetween2Vecs(vec_cb, vec_cd))
    #cda
    vec_dc = Point(Q[2].x-Q[3].x, Q[2].y-Q[3].y)
    vec_da = Point(Q[0].x-Q[3].x, Q[0].y-Q[3].y)
    angles.append(AngleBetween2Vecs(vec_dc, vec_da))

    for a in angles:
        if a < 80 or a > 100:
            return False
    return True

def checkAspectRatio(Q):
    normL = []
    normL.append(np.linalg.norm([Q[1].x - Q[0].x, Q[1].y - Q[0].y]))
    normL.append(np.linalg.norm([Q[2].x - Q[1].x, Q[2].y - Q[1].y]))
    normL.append(np.linalg.norm([Q[3].x - Q[2].x, Q[3].y - Q[2].y]))
    normL.append(np.linalg.norm([Q[0].x - Q[3].x, Q[0].y - Q[3].y]))
    aspect = np.min(normL)/ np.max(normL)
    #print "aspect:%s" % aspect
    if aspect < 0.45 or aspect > 0.85:
        return False
    else:
        return True



def intersection_between_lines(la,lb):

    la_start = Point(la[0], la[1])
    la_end = Point(la[2], la[3])

    lb_start = Point(lb[0], lb[1])
    lb_end = Point(lb[2], lb[3])

    X1 = la_end.x - la_start.x
    Y1 = la_end.y - la_start.y

    X2 = lb_end.x - lb_start.x
    Y2 = lb_end.y - lb_start.y

    X21 = lb_start.x - la_start.x
    Y21 = lb_start.y - la_start.y

    D = Y1 * X2 - Y2 * X1

    if D == 0:
        return Point(0,0)

    ptx = (X1 * X2 * Y21 + Y1 * X2 * la_start.x - Y2 * X1 * lb_start.x) / D;
    pty = -(Y1 * Y2 * X21 + X1 * Y2 * la_start.y - X2 * Y1 * lb_start.y) / D;
    pt = Point(ptx, pty)

    c1 = abs(pt.x - la_start.x - round(X1 / 2)) <= abs(round(X1 / 2))
    c2 = abs(pt.y - la_start.y - round(Y1 / 2)) <= abs(round(Y1 / 2))
    c3 = abs(pt.x - lb_start.x - round(X2 / 2)) <= abs(round(X2 / 2))
    c4 = abs(pt.y - lb_start.y - round(Y2 / 2)) <= abs(round(Y2 / 2))

    #if c1 and c2 and c3 and c4:
    return pt
    #else:
    #return Point(0, 0)


def houghSpace_to_cartesian_vec4(l):
    rho = l[0]
    theta = l[1]
    a = np.cos(theta)
    b = np.sin(theta)
    x0 = a * rho
    y0 = b * rho
    x1 = int(x0 + 1000 * (-b))
    y1 = int(y0 + 1000 * a)
    x2 = int(x0 - 1000 * (-b))
    y2 = int(y0 - 1000 * a)
    return [x1, y1, x2, y2]


def make_quadrangle(left,top,right,down):
    corner = []
    corner.append(intersection_between_lines(left, top))
    corner.append(intersection_between_lines(top, right))
    corner.append(intersection_between_lines(right, down))
    corner.append(intersection_between_lines(down, left))
    for c in corner:
        if c.x == 0 and c.y == 0:
            corner = []
            break
    return corner


def print_q(Q):
    for p in Q:
        print ', '.join(['%s:%s' % item for item in p.__dict__.items()])


def largest_quadrangle_search(horizontal_lines, vertical_lines, img):
    # type: (object, object, object) -> object
    areaThres = img.shape[0] * img.shape[1] / 4
    max_area = areaThres  # area thres:  1/3 * area(img)
    bestQ = None
    for l in range(len(vertical_lines)):
        for t in range(len(horizontal_lines)):
            for r in range(l+1, len(vertical_lines)):
                for d in range(t+1, len(horizontal_lines)):
                    left_vec4 = houghSpace_to_cartesian_vec4(vertical_lines[l])
                    top_vec4 = houghSpace_to_cartesian_vec4(horizontal_lines[t])
                    right_vec4 = houghSpace_to_cartesian_vec4(vertical_lines[r])
                    down_vec4 = houghSpace_to_cartesian_vec4(horizontal_lines[d])
                    Q = make_quadrangle(left_vec4, top_vec4, right_vec4, down_vec4)
                    if len(Q) == 4:
                        #print 'up-left:%s,up-right:%s,down-right:%s,down-left:%s' \
                        #     % ((Q[0].x,Q[0].y), (Q[1].x, Q[1].y), (Q[2].x,Q[2].y), (Q[3].x,Q[3].y))

                        area = quadArea(Q)
                        if area > max_area:
                            if check_angle(Q) and checkAspectRatio(Q) \
                                    and checkByBoundarayCondition(Q, img.shape[1], img.shape[0]):
                                max_area = area
                                bestQ = Q
    #print "maxArea:%s" % max_area
    if max_area > areaThres:
        #if Q:
        #    print_q(Q)
        return bestQ, max_area
    else:
        return None, max_area


