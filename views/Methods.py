import pickle
import cv2
from sklearn.externals import joblib
from skimage.feature import hog
import numpy as np
from sklearn import linear_model
import json
import requests
from urllib import request
import hashlib

myapiKey = 'AIzaSyDyn8Fg0lDikUh1fCrruKDioiDi_OpvkDQ'
mycx = '000804340759888014000%3Awzsy93prchc'



def hogIsle(classifierPath, myfile):
    clf = joblib.load("Resources/digits_cls.pkl")
    im = cv2.imread(myfile)
    im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im_gray = cv2.GaussianBlur(im_gray, (5, 5), 0)
    ret, im_th = cv2.threshold(im_gray, 90, 255, cv2.THRESH_BINARY_INV)
    im_th, ctrs, hier = cv2.findContours(im_th.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = [cv2.boundingRect(ctr) for ctr in ctrs]
    rects = sorted(rects, key=lambda tup: (tup[0], tup[1]))
    resultString = ''
    for rect in rects:
        try:
            cv2.rectangle(im, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (0, 255, 0), 3)
            leng = int(rect[3] * 1.6)
            pt1 = int(rect[1] + rect[3] // 2 - leng // 2)
            pt2 = int(rect[0] + rect[2] // 2 - leng // 2)
            roi = im_th[pt1:pt1 + leng, pt2:pt2 + leng]
            # Resize image
            roi = cv2.resize(roi, (28, 28), interpolation=cv2.INTER_AREA)
            roi = cv2.dilate(roi, (3, 3))

            roi_hog_fd = hog(roi, orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
            nbr = clf.predict(np.array([roi_hog_fd], 'float64'))
            #print(str(int(nbr[0])))
            resultString += str(int(nbr[0]))+','
            cv2.putText(im, str(int(nbr[0])), (rect[0], rect[1]), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 0), 1)
        except:
            pass
    return im, resultString


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts) ]

def resimUzerindeNoktalariGoster(path,listim):
    image = cv2.imread(path)
    if type(image) is not np.array:
        image = np.array(image)
    overlay = image.copy()
    alpha = 0.7
    for point in listim:
        cv2.line(overlay, (point.pointX, point.pointY), (point.otherFeature.pointX, point.otherFeature.pointY),
                 (0, 255, 0))
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)
    return image

def findInlierPointsWithRansac(listim):
    try:
        source_points = []
        destination_points = []

        for featurem in listim:
            source_points.append([featurem.pointY, featurem.pointX])
            destination_points.append([featurem.otherFeature.pointY, featurem.otherFeature.pointX])

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
            ransacFeatureListim.append(listim[i])
        return ransacFeatureListim
    except:
        return None

def getPicturesFromGoogleCustomSearch(word):
    resimList = []
    for start in range(1,50,1):
        try:
            url = "https://www.googleapis.com/customsearch/v1?key={}&cx={}&q={}&filter=1&start={}&num=10&alt=json&searchType=image".format(myapiKey, mycx,
                                                                                                                                           word, start)
            t = requests.get(url)
            gelenDatalar = json.loads(t.text)

            if gelenDatalar is not None:
                if 'items' in gelenDatalar:
                    items = gelenDatalar['items']
                    if items is not None:
                        for item in items:
                            try:
                                 image_link = item['link']
                                 temp_dosyasi = request.urlretrieve(image_link) # bu sekilde tempe aliyor.
                                 resmim = cv2.imread(temp_dosyasi[0])
                                 resimList.append(resmim)
                            except:
                                pass
        except:
            pass
    return resimList

def findMatchesWithSIFT(img1,img2):
    try:
        grayImg1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        grayImg2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        orb = cv2.xfeatures2d.SIFT_create()
        # find the keypoints and descriptors with SIFT
        kp1, des1 = orb.detectAndCompute(grayImg1, None)
        kp2, des2 = orb.detectAndCompute(grayImg2, None)
        # create BFMatcher object
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        # Apply ratio test
        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append([m])

        img3 = cv2.drawMatchesKnn(img1, kp1, img2, kp2, good,None, flags=2)

        return good,img3
    except BaseException as e:
        print(str(e))
        return None

def computeMD5hash(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

def saveImageToFile(filePath,image):
    try:
        cv2.imwrite(filePath,image)
    except BaseException as e:
        print(str(e))

def pickleOlustur(fileName,object,method=None):
    try:
        if method is None:
            with open(fileName, 'w') as fp:
                json.dump(object, fp)
        elif method == 1:
                joblib.dump(object, fileName)
        return '0'
    except BaseException as e:
        print(str(e))
        return '-1'

def pickleYukle(fileName,method=None):
    #data =joblib.load(fileName)
    if method is None:
        with open(fileName, 'r') as fp:
            data = json.loads(fp.read())
    elif method == 1:
        data =joblib.load(fileName)
    return data


def resizeImage(image,newWidth,newHeight):
    try:
        if len(image.shape)==2:
            height, width = image.shape
        else:
            height, width,channels = image.shape
        oranHeight, oranWidth = 1, 1
        if height > newHeight:
            oranHeight = height / newHeight
        if width > newWidth:
            oranWidth = width / newWidth
        height = height / oranHeight
        width = width / oranWidth
        imageReturn = image.copy()
        imageReturn = cv2.resize(imageReturn, (int(width), int(height)), interpolation=cv2.INTER_CUBIC)
        return imageReturn
    except:
        return image



def intTryParse(value):
    try:
        return int(value), True
    except ValueError:
        return value, False

