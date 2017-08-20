import numpy as np
import cv2
import sys
import math
from PIL import Image
import matplotlib.pyplot as plt
from scipy.special import entr
import scipy.stats as ss
import operator #sortlama icin kullancam bunu
import collections
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from classes import cs_Feature
from skimage import feature


def CannyEdgeDetector(path,patchSize):
    filename = path
    img = cv2.imread(filename)       
    yeniPatchSize = int(patchSize/2)
    featureList=[]
    if img is not None:
       gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
       #gray_Canny = feature.canny(gray)
       gray_Canny = cv2.Canny(img,200,300)
       px = 'D:/Python_Kodlar/Phyton_Image_Processing/Phyton_Image_Processing/Phyton_Image_Processing/Images/Canny-{}'.format(path[-9:])
       cv2.imwrite(px,gray_Canny)
       hei,wi = gray_Canny.shape
       for y in range(0,hei):
            for x in range(0,wi):
                try:
                    if not (yeniPatchSize<x<wi-yeniPatchSize and yeniPatchSize<y<hei-yeniPatchSize and gray_Canny[y,x]==255):
                        continue
                    roi = gray[y-yeniPatchSize:y+yeniPatchSize+1,x-yeniPatchSize:x+yeniPatchSize+1]  # roi grayden gelicek
                    my_Feature = cs_Feature.Feature(x,y,roi)
                    featureList.append(my_Feature)
                except BaseException as e: 
                    print(" Blok Olusturma hata - {}" ,str(e))
                    pass
    return featureList




def  Sift(path,patchSize):
     img =cv2.imread(path)
     height,width,channel = img.shape
     gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
     sift = cv2.xfeatures2d.SIFT_create()
     kp = sift.detect(gray,None)
     cv2.drawKeypoints(gray,kp,img)
     featureList = []
     yeniPatchSize = int(patchSize/2 )
     for i in kp:
         wi  = int(i.pt[0])
         hei = int(i.pt[1])
         kontrol = list(filter(lambda x: x.pointX==wi and x.pointY==hei ,featureList))
         if len(kontrol)==0:		 
            if not (yeniPatchSize<wi<width-yeniPatchSize and yeniPatchSize<hei<height-yeniPatchSize):
                 continue
            roi = gray[hei-yeniPatchSize:hei+yeniPatchSize+1,wi-yeniPatchSize:wi+yeniPatchSize+1]  # roi grayden gelicek
            my_Feature = cs_Feature.Feature(wi, hei, roi)
            featureList.append(my_Feature)
     return featureList




        
            
       
                




 