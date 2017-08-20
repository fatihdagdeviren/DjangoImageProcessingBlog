import cv2
import numpy as np
from sklearn import linear_model
import os

def sift_surf_knn(path, thresholdForMinNeigbour=None, thresholdForMinDistance=None):
    try:
        img = cv2.imread(path)
        image2 = cv2.imread(path)
        height, width, channel = img.shape
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sift = cv2.xfeatures2d.SIFT_create()
        kp = sift.detect(gray, None)
        imgdraw = img.copy()
        graydraw = gray.copy()
        cv2.drawKeypoints(graydraw, kp, imgdraw)
        siftDescriptor = cv2.xfeatures2d.SURF_create()
        keyPoints, descriptors = siftDescriptor.compute(img, kp)
        keyPoints2 = keyPoints.copy()
        descriptors2 = descriptors.copy()

        bf = cv2.BFMatcher()
        matches = bf.knnMatch(descriptors, descriptors2, k=3)  # en yakin 2 nokta, ilki hep kendisi oluyor zaten.

        good = []
        silinecek_indexList = []
        if thresholdForMinDistance is not None:
            for index in range(0, len(matches)):
                eslesenler = matches[index][1]
                kp1 = keyPoints[eslesenler.queryIdx]
                kp2 = keyPoints2[eslesenler.trainIdx]
                # noktalari aliyorum burada
                wi_1 = int(kp1.pt[0])
                hei_1 = int(kp1.pt[1])
                wi_2 = int(kp2.pt[0])
                hei_2 = int(kp2.pt[1])
                uzaklik = ((wi_1 - wi_2) ** 2 + (hei_1 - hei_2) ** 2) ** 0.5
                if uzaklik <= thresholdForMinDistance:
                    silinecek_indexList.append(index)

        if thresholdForMinNeigbour is not None:
            for index in range(0, len(matches)):
                kendisi, m, n = matches[index]
                if m.distance >= thresholdForMinNeigbour * n.distance:
                    silinecek_indexList.append(index)

        if len(silinecek_indexList) > 0:
            silinecek_indexList = list(set(silinecek_indexList))  # listeyi unique hale getiriyorumki ayni degerler elensin.
            for index in range(0, len(matches)):
                if index not in silinecek_indexList:
                    good.append(matches[index])
        if len(good) > 0:
            matches = []
            matches = good

        if type(img) is not np.array:
            img = np.array(img)
        overlay = img.copy()
        ransacImage = img.copy()

        alpha = 0.7

        source_points = []
        destination_points = []

        for match in matches:
            eslesenler = match[1]
            kp1 = keyPoints[eslesenler.queryIdx]
            kp2 = keyPoints2[eslesenler.trainIdx]
            # noktalari aliyorum burada
            wi_1 = int(kp1.pt[0])
            hei_1 = int(kp1.pt[1])
            wi_2 = int(kp2.pt[0])
            hei_2 = int(kp2.pt[1])
            source_points.append([hei_1, wi_1])
            destination_points.append([hei_2, wi_2])
            # cv2.circle(overlay, (int(featurem.pointX), int(featurem.pointY)), int(patchSize/2), (0, 255, 0), -1)
            # cv2.circle(overlay, (wi+int(featurem.otherFeatures[0].pointX), int(featurem.otherFeatures[0].pointY)), int(patchSize/2), (0, 255, 0), -1)
            cv2.line(overlay, (wi_1, hei_1), (wi_2, hei_2), (0, 255, 0))
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)


        # estimate affine transform model using all coordinates
        model = linear_model.RANSACRegressor(linear_model.LinearRegression())
        source_points = np.array(source_points)
        destination_points = np.array(destination_points)
        model.fit(source_points, destination_points)

        # robustly estimate affine transform model with RANSAC
        inliers = model.inlier_mask_
        outliers = inliers == False
        inlier_idxs = np.nonzero(inliers)[0]
        ransacFeatureListim = []

        for i in inlier_idxs:
            eslesenler = matches[i][1]
            kp1 = keyPoints[eslesenler.queryIdx]
            kp2 = keyPoints2[eslesenler.trainIdx]
            # noktalari aliyorum burada
            wi_1 = int(kp1.pt[0])
            hei_1 = int(kp1.pt[1])
            wi_2 = int(kp2.pt[0])
            hei_2 = int(kp2.pt[1])
            cv2.line(ransacImage, (wi_1, hei_1), (wi_2, hei_2), (0, 255, 0))
        cv2.addWeighted(ransacImage, alpha, image2, 1 - alpha, 0, image2)
        # cv2.imwrite('{0}\Ransacli_{1}'.format(directoryName, resimIndex), image2)
        return  img,image2
    except BaseException as e:
        print(" hata - {}", str(e))
        pass  # endregion