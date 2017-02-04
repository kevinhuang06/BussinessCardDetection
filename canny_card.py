
import cv2
import glob
import os

img_inputpath = []
canny_outputpath = []
def cannyCard():
    for ipath in glob.glob("/Users/kevinhuang/PycharmProjects/cardDetect2/jiandongCard/*.JPG"):
        print ipath
        bname = os.path.basename(ipath)
        _outputpath = os.path.join("/Users/kevinhuang/PycharmProjects/cardDetect2/canny_jiandongCard/", bname)
        img = cv2.imread(ipath)

        small = cv2.resize(img, (int(img.shape[1] / 6), int(img.shape[0] / 6)))
        # print small.shape

        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        # print "cost %s second"%( time.clock() - start)
        gray = cv2.bilateralFilter(gray, 5, 50, 50)
        img_bw = cv2.Canny(gray, 50, 150)
        cv2.imwrite(_outputpath, img_bw)

cannyCard()


