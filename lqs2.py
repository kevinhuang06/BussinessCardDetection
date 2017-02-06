
import numpy as np


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def area_of_quadrangle(quad):

    x1 = quad[2].x - quad[0].x
    y1 = quad[2].y - quad[0].y
    x2 = quad[3].x - quad[1].x
    y2 = quad[3].y - quad[1].y

    return abs(x1*y2 - x2*y1)/2


def angle_between_two_vectors(va, vb):

    inter_product = va.x * vb.x + va.y * vb.y
    va_module = np.sqrt(np.power(va.x, 2) + np.power(va.y, 2))
    vb_module = np.sqrt(np.power(vb.x, 2) + np.power(vb.y, 2))
    cos_ab = inter_product / (vb_module * va_module)

    return np.arccos(cos_ab)*180/np.pi


def check_angle(quad):

    angles = []
    # dab
    vec_ad = Point(quad[3].x - quad[0].x, quad[3].y - quad[0].y)
    vec_ab = Point(quad[1].x - quad[0].x, quad[1].y - quad[0].y)
    angles.append(angle_between_two_vectors(vec_ad, vec_ab))
    # abc
    vec_ba = Point(quad[0].x - quad[1].x, quad[0].y - quad[1].y)
    vec_bc = Point(quad[2].x - quad[1].x, quad[2].y - quad[1].y)
    angles.append(angle_between_two_vectors(vec_ba, vec_bc))
    # bcd
    vec_cb = Point(quad[1].x - quad[2].x, quad[1].y - quad[2].y)
    vec_cd = Point(quad[3].x - quad[2].x, quad[3].y - quad[2].y)
    angles.append(angle_between_two_vectors(vec_cb, vec_cd))
    # cda
    vec_dc = Point(quad[2].x - quad[3].x, quad[2].y - quad[3].y)
    vec_da = Point(quad[0].x - quad[3].x, quad[0].y - quad[3].y)
    angles.append(angle_between_two_vectors(vec_dc, vec_da))

    for a in angles:
        if a < 80 or a > 100:
            return False
    return True


def check_boundary(quad, cols, rows):
    for p in quad:
        if p.x < 0 or p.x > cols or p.y < 0 or p.y > rows:
            return False
    return True


def check_aspect_ratio(quad):

    norm2 = []
    norm2.append(np.linalg.norm([quad[1].x - quad[0].x, quad[1].y - quad[0].y]))
    norm2.append(np.linalg.norm([quad[2].x - quad[1].x, quad[2].y - quad[1].y]))
    norm2.append(np.linalg.norm([quad[3].x - quad[2].x, quad[3].y - quad[2].y]))
    norm2.append(np.linalg.norm([quad[0].x - quad[3].x, quad[0].y - quad[3].y]))

    aspect = np.min(norm2) / np.max(norm2)
    if aspect < 0.45 or aspect > 0.85:
        return False
    else:
        return True


def intersection_between_lines(la, lb):

    la_start = la[0]
    la_end = la[1]

    lb_start = lb[0]
    lb_end = lb[1]

    p1 = Point(la_end.x - la_start.x, la_end.y - la_start.y)
    p2 = Point(lb_end.x - lb_start.x, lb_end.y - lb_start.y)
    p21 = Point(lb_start.x - la_start.x, lb_start.y - la_start.y)

    d = p1.y * p2.x - p2.y * p1.x

    if d == 0:
        return Point(-1, -1)

    ptx = (p1.x * p2.x * p21.y + p1.y * p2.x * la_start.x - p2.y * p1.x * lb_start.x) / d
    pty = -(p1.y * p2.y * p21.x + p1.x * p2.y * la_start.y - p2.x * p1.y * lb_start.y) / d

    pt = Point(ptx, pty)

    c1 = abs(pt.x - la_start.x - round(p1.x / 2)) <= abs(round(p1.x / 2))
    c2 = abs(pt.y - la_start.y - round(p1.y / 2)) <= abs(round(p1.y / 2))
    c3 = abs(pt.x - lb_start.x - round(p2.x / 2)) <= abs(round(p2.x / 2))
    c4 = abs(pt.y - lb_start.y - round(p2.y / 2)) <= abs(round(p2.y / 2))

    #if c1 and c2 and c3 and c4:
    return pt
    #else:
    #return Point(-1, -1)


def express_line_with_two_points(lines):

    new_lines = []
    for l in lines:
        rho = l[0]
        theta = l[1]

        p0 = Point(rho * np.cos(theta), rho * np.sin(theta))
        p1 = Point(int(p0.x - 1000 * np.sin(theta))
                   , int(p0.y + 1000 * np.cos(theta)))
        p2 = Point(int(p0.x + 1000 * np.sin(theta))
                   , int(p0.y - 1000 * np.cos(theta)))

        new_lines.append([p1, p2])

    return new_lines


def make_quadrangle(bottom, left, top, right):

    corner = []
    corner.append(intersection_between_lines(bottom, left))
    corner.append(intersection_between_lines(left, top))
    corner.append(intersection_between_lines(top, right))
    corner.append(intersection_between_lines(right, bottom))

    for c in corner:
        if c.x == 0 and c.y == 0:
            corner = []
            break
    return corner


def largest_quadrangle_search(vertical_lines, horizon_lines, cols, rows):

    area_threshold = rows * cols / 4
    max_area = area_threshold
    best_quad = []
    v_lines = express_line_with_two_points(vertical_lines)
    h_lines = express_line_with_two_points(horizon_lines)

    for b in range(len(h_lines)):
        for l in range(len(v_lines)):
            for t in range(b + 1, len(h_lines))[::-1]:
                for r in range(l+1, len(v_lines))[::-1]:

                    quad = make_quadrangle(h_lines[b], v_lines[l], h_lines[t], v_lines[r])
                    if quad:
                        area = area_of_quadrangle(quad)
                        if area > max_area:
                            if check_angle(quad) and check_aspect_ratio(quad) \
                                    and check_boundary(quad, cols, rows):
                                max_area = area
                                best_quad = quad

    return [[p.x, p.y] for p in best_quad]


