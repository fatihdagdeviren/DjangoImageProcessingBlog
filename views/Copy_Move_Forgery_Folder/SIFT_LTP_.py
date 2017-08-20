import numpy as np
from sklearn import linear_model
import cv2
import views.Copy_Move_Forgery_Folder.LocalTernaryPattern_FM as mlbp
from views import CornerDetectionModule as cdm

def sift_ltp(image_file_path, patchSize, thresholdForMinNeighbour, thresholdForMinDistance,ThresholdForGLCM=None):
    try:
            komsulukListesiSayisi = 10
            featureListim = cdm.Sift(image_file_path,patchSize)
            koorListim,ltpCodeListim = mlbp.bolgeleriOlustur(featureListim,5,komsulukListesiSayisi,threholdForGLCM=ThresholdForGLCM) # 5 degeri burada -1,1 araliginda ltp stringi olusturulurken kullaniyorum.
            result = mlbp.bolgeleriEslestir(koorListim,ltpCodeListim, thresholdForMinDistance, thresholdForMinNeighbour)  # onceki 0.7 yyine

            if len(result)>0:
                # Buradan sonra yazmaya basliyorum.
                img = cv2.imread(image_file_path)
                img2=img.copy()
                overlay = img.copy()
                ransacImage = img.copy()
                alpha = 0.7
                #region RansacIslemleri
                source_points=[]
                destination_points=[]
                for eslesimler in result:
                    source_points.append([featureListim[eslesimler[0]].pointY,featureListim[eslesimler[0]].pointX])
                    destination_points.append([featureListim[eslesimler[1]].pointY,featureListim[eslesimler[1]].pointX])
                    cv2.line(overlay, (featureListim[eslesimler[0]].pointX, featureListim[eslesimler[0]].pointY), (featureListim[eslesimler[1]].pointX, featureListim[eslesimler[1]].pointY), (0, 255, 0))
                cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)



                # estimate affine transform model using all coordinates
                model = linear_model.RANSACRegressor(linear_model.LinearRegression())
                source_points = np.array(source_points)
                destination_points = np.array(destination_points)
                model.fit(source_points, destination_points )
                # robustly estimate affine transform model with RANSAC
                inliers = model.inlier_mask_
                if len(inliers)>0:
                    outliers = inliers == False
                    inlier_idxs = np.nonzero(inliers)[0]
                    ransacFeatureListim=[]
                    for i in inlier_idxs:
                        #ransacFeatureListim.append(featureListim[i]) ilerde acilabilir.
                        cv2.line(ransacImage, (featureListim[result[i][0]].pointX, featureListim[result[i][0]].pointY), (featureListim[result[i][1]].pointX, featureListim[result[i][1]].pointY), (0, 255, 0))
                    cv2.addWeighted(ransacImage, alpha, img2, 1 - alpha, 0, img2)
                return img,img2
                #endregion
    except BaseException as e:
            print(" hata - {}".format(str(e)))
            pass

#endregion









