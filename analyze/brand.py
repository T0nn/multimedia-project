from contentdetector import ContentDetector
import numpy as np
import time
import math
import cv2
import multiprocessing as mp

class Image:
    def __init__(self, index, data):
        self.index = index
        self.data = data

def isconvex(boarder,height=270,width=480):
    x1 = boarder[0][0][0]
    y1 = boarder[0][0][1]
    x2 = boarder[0][3][0]
    y2 = boarder[0][3][1]
    x3 = boarder[0][1][0]
    y3 = boarder[0][1][1]
    x4 = boarder[0][2][0]
    y4 = boarder[0][2][1]
    if x1>0 and x1<width and x2>0 and x2<width and x3>0 and x3<width and x4>0 and x4<width and y1>0 and y1<height and y2>0 and y2<height and y3>0 and y3<height and y4>0 and y4<height:
        z1 = ((x2 - x1) * (y4 - y1) - (x4 - x1) * (y2 - y1))
        z2 = ((x4 - x1) * (y3 - y1) - (x3 - x1) * (y4 - y1))
        z3 = ((x4 - x2) * (y3 - y2) - (x3 - x2) * (y4 - y2))
        z4 = ((x3 - x2) * (y1 - y2) - (x1 - x2) * (y3 - y2))
        return (z1 * z2) > 0 and (z3 * z4) > 0
    else:
        return False

def siftdetector(ad_logo):
    height = 270
    width = 480
    channel = 3
    sift = cv2.xfeatures2d.SIFT_create()
    trainImg = np.zeros((len(ad_logo), height, width), dtype=np.uint8)
    trainKP = []
    trainDesc = []

    for i in range(len(trainImg)):
        with open(ad_logo[i], "rb") as f:
            Img = f.read()
            Img = np.frombuffer(Img, dtype=np.uint8)
            Img = Img.reshape((channel, -1))
            Img = Img.transpose()
            Img = Img.reshape((height, width, channel))
            trainImg[i] = cv2.cvtColor(Img, cv2.COLOR_RGB2GRAY)

    for i in range(len(ad_logo)):
        kp, desc = sift.detectAndCompute(trainImg[i], None)
        pts = [p.pt for p in kp]
        trainKP.append(pts)
        #trainKP.append(kp)
        trainDesc.append(desc)

    return trainKP, trainDesc

def brandmatch(index, trainKP, trainDesc, QueryImgRGB, height=270, width=480):

    MIN_MATCH_COUNT = 12
    sift = cv2.xfeatures2d.SIFT_create()
    FLANN_INDEX_KDITREE = 0
    flannParam = dict(algorithm=FLANN_INDEX_KDITREE, tree=5)
    flann = cv2.FlannBasedMatcher(flannParam, {})
    QueryImgBGR = cv2.cvtColor(QueryImgRGB, cv2.COLOR_RGB2BGR)
    QueryImg = cv2.cvtColor(QueryImgBGR, cv2.COLOR_BGR2GRAY)
    queryKP, queryDesc = sift.detectAndCompute(QueryImg, None)

    for i in range(len(trainKP)):
        ##recognize brand##
        matches = flann.knnMatch(queryDesc, trainDesc[i], k=2)

        goodMatch = []
        for m, n in matches:
            if (m.distance < 0.75 * n.distance):
                goodMatch.append(m)
        if (len(goodMatch) > MIN_MATCH_COUNT):
            tp = []
            qp = []
            for m in goodMatch:
                #tp.append(trainKP[i][m.trainIdx].pt)
                tp.append(trainKP[i][m.trainIdx])
                qp.append(queryKP[m.queryIdx].pt)
            tp, qp = np.float32((tp, qp))
            H, status = cv2.findHomography(tp, qp, cv2.RANSAC, 3.0)
            h = height
            w = width
            trainBorder = np.float32([[[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]])
            if H is not None:
                queryBorder = cv2.perspectiveTransform(trainBorder, H)
                if isconvex(queryBorder):
                    print(queryBorder)
                    QueryImgBGR = QueryImgBGR.copy()
                    cv2.polylines(QueryImgBGR, [np.int32(queryBorder)], True, (0, 255, 0), 2)
                    cv2.imwrite("./" + str(index) + "_framenumber.png", QueryImgBGR)

                else:
                    print("Not Enough match found- %d/%d" % (len(goodMatch), MIN_MATCH_COUNT))
        if len(goodMatch) <= MIN_MATCH_COUNT:
            print("Not Enough match found- %d/%d" % (len(goodMatch), MIN_MATCH_COUNT))
    cv2.imshow('result'+ str(mp.current_process()), QueryImgBGR)
    cv2.waitKey(1)
    img = cv2.cvtColor(QueryImgBGR, cv2.COLOR_BGR2RGB)
    result = Image(index,img)
    return result

