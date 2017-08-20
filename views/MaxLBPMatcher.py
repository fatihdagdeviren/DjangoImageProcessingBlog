import numpy as np
import cv2
import sys
import math
from PIL import Image
import matplotlib.pyplot as plt
from scipy.special import entr
import scipy.stats as ss
import operator  # sortlama icin kullanicam bunu
import collections
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from classes.cs_Feature import *
from skimage.feature import greycomatrix, greycoprops
from skimage.feature import greycomatrix, greycoprops
from skimage import data
from scipy.stats.stats import pearsonr


def shift(seq, n):
    n = n % len(seq)
    return seq[n:] + seq[:n]


def bolgeleriOlustur(featureListim, thresholdForltp):
    for feature in featureListim:
        try:
            glcmTextureLarim = glcmOlustur(feature.patchData)  # 0,45,90 ve 135 sirasiyla
            hei, wi = feature.patchData.shape
            rowSayisi = int(hei / 3)
            colSayisi = int(wi / 3)  # genelde bunlarin 2 si esit olucak.
            bolgelerim = []
            index = 0
            vektorDatam = []
            toplamDonguSayisi = math.floor(hei / 6) + 1  # +1 merkez icin
            gidilecekSayi = int(hei / 3)  # her seferinde 2 azalticam burayi
            icHIndex = 1
            for i in range(1, toplamDonguSayisi + 1):
                try:
                    katmanBolgem = []
                    icWIndex = icHIndex
                    ustBolgelerim = []
                    if icHIndex == (hei - 1) / 2:  # merkeze geldik
                        datam = feature.patchData[icHIndex - 1:icHIndex + 2, icWIndex - 1:icWIndex + 2]
                        katmanBolgem.extend([[icHIndex, icHIndex], datam, feature.patchData[icHIndex, icWIndex]])
                        vektorDatam.append(katmanBolgem)
                        break

                    for m_ust in range(0, gidilecekSayi - 1):
                        datam = feature.patchData[icHIndex - 1:icHIndex + 2, icWIndex - 1:icWIndex + 2]  # +2 diyorum dahil degil cunku
                        ustBolgelerim.append([[icHIndex, icWIndex], datam, feature.patchData[icHIndex, icWIndex]])
                        icWIndex += 3  # bir sonraki merkez indexi icin

                    sonEklenen = ustBolgelerim[-1]  # asagiya dogru inicem ondan dolayı widthi kullanicam.
                    sagH = sonEklenen[0][0]
                    sagW = sonEklenen[0][1] + 3
                    sagBolgelerim = []
                    sagBolgelerim.append([[sagH, sagW], feature.patchData[sagH - 1:sagH + 2, sagW - 1:sagW + 2], feature.patchData[sagH, sagW]])
                    for m_sag in range(0, gidilecekSayi - 1):
                        sagH += 3
                        datam = feature.patchData[sagH - 1:sagH + 2, sagW - 1:sagW + 2]  # +2 diyorum dahil degil cunku
                        sagBolgelerim.append([[sagH, sagW], datam, feature.patchData[sagH, sagW]])

                    sonEklenen = sagBolgelerim[-1]
                    altH = sonEklenen[0][0]
                    altW = sonEklenen[0][1]
                    altBolgelerim = []
                    # altBolgelerim.append([[altH,altW],feature.patchData[altH-1:altH+2,altW-1:altW+2]])
                    for m_alt in range(0, gidilecekSayi - 1):
                        # height sabit width azalicak.
                        altW -= 3
                        altBolgelerim.append([[altH, altW], feature.patchData[altH - 1:altH + 2, altW - 1:altW + 2], feature.patchData[altH, altW]])

                    sonEklenen = altBolgelerim[-1]
                    solH = sonEklenen[0][0]
                    solW = sonEklenen[0][1]
                    solBolgelerim = []
                    # solBolgelerim.append([[solH,solW],feature.patchData[solH-1:solH+2,solW-1:solW+2]])
                    for m_sol in range(0, gidilecekSayi - 2):  # ilkini aldigim icin -2 gidiyorum
                        # width sabit height azalicak
                        solH -= 3
                        solBolgelerim.append([[solH, solW], feature.patchData[solH - 1:solH + 2, solW - 1:solW + 2], feature.patchData[solH, solW]])
                    katmanBolgem.extend(ustBolgelerim)
                    katmanBolgem.extend(sagBolgelerim)
                    katmanBolgem.extend(altBolgelerim)
                    katmanBolgem.extend(solBolgelerim)  # belki ilerde katmanbolgemi shift edebiliriz. su an sadece ic bolgeyi ediyoruz.
                    vektorDatam.append(katmanBolgem)
                    icHIndex += 3
                    gidilecekSayi -= 2
                except:
                    print('hata')

            merkezim = vektorDatam[-1]
            lbpStringim = []
            for m_v in range(0, len(vektorDatam) - 1):
                # merkez ile hepsini karsilastiricam,en buyuk basa shift edicek.
                katmanDatalari = vektorDatam[m_v]
                for katman in katmanDatalari:
                    resultL = ltpStringGetir(katman, thresholdForltp)
                    lbpStringim.extend(resultL)

            lbpDatam = ltpStringGetir(merkezim, thresholdForltp)
            lbpStringim.extend(lbpDatam)
            # x = lbpStringim
            # bir bolge icin, alt bogeler olustu shift etti ve kendi icleride shift etti artık herbiri icin lbp stringlerini üretebilirim sanirim.
            feature.vektorData = lbpStringim  # -1,0,1 iceren bir liste bunun benzerligine bakicam. birbirinden cikarirsan bunları 0 olan yerlerin sayisi / toplam uzunluk guzel olabilirmi?
            feature.glcmTexturelarim = glcmTextureLarim
        except BaseException as e:
            print(" feature olusturuken hata - {}", str(e))
            pass


def ltpStringGetir(datam, thresholdForltp):
    yeniList = []
    yeniList.append(datam[1][0][0])
    yeniList.append(datam[1][0][1])
    yeniList.append(datam[1][0][2])
    yeniList.append(datam[1][1][2])
    yeniList.append(datam[1][2][2])
    yeniList.append(datam[1][2][1])
    yeniList.append(datam[1][2][0])
    yeniList.append(datam[1][1][0])  # 1,1 merkez almayacagim.
    merkezim = datam[2]
    merkez_maksNerde = np.argmax(yeniList)
    if merkez_maksNerde > 0:  # kaykil bakam
        temp_d = shift(yeniList, merkez_maksNerde)
        datam[1] = temp_d
    else:
        datam[1] = yeniList
    lbpVektor_merkez = []
    for lbp in datam[1]:
        if lbp <= merkezim - thresholdForltp:
            lbpVektor_merkez.append(-1)
        elif merkezim - thresholdForltp < lbp < merkezim + thresholdForltp:
            lbpVektor_merkez.append(0)
        else:
            lbpVektor_merkez.append(1)
    return lbpVektor_merkez


def bolgeleriEslestir_With_List(featureListim, thresholdDistance, correlationCoefficent, thresholdForGLCM=None):
    # buraya liste iceren liste gondericem bu sekilde ilerde hizlandiricam ve threadli calisma yapabilmeyi umuyorum.
    resultList = []  # -1 iceren list olusturuyorum
    for i in range(0, len(featureListim)):
        point1 = featureListim[i][0]  # koordinatlar gelicek burdan
        vektorData1 = featureListim[i][1]
        glcmTexturem1 = featureListim[i][2]
        resultList.append([featureListim[i][0], -1, -1])
        for j in range(0, len(featureListim)):
            point2 = featureListim[j][0]  # koordinatlar gelicek burdan
            vektorData2 = featureListim[j][1]
            glcmTexturem2 = featureListim[j][2]
            if thresholdForGLCM is not None:
                # contrastValue = 0
                dissim, correlation, contrast, energy, ASM = thresholdForGLCM
                glcmDegerler = glcmDegerleriDondur(glcmTexturem1[0], glcmTexturem2[0])
                if not (int(glcmDegerler[0]) <= int(dissim) and int(glcmDegerler[1]) <= int(correlation) and int(glcmDegerler[2]) <= int(
                        contrast) and int(glcmDegerler[3]) <= int(energy)
                        and int(glcmDegerler[4]) <= int(ASM)):
                    continue
            distance = ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
            if distance >= thresholdDistance:
                farkList = [(x1 - x2) for (x1, x2) in zip(vektorData1[0], vektorData2[0])]
                sifirCount = len(list(filter(lambda x: x == 0, farkList)))
                # ortalamaCorrelation = correlationCoeffGetir(vektorData1,vektorData2)
                ortalamaCorrelation = sifirCount / len(farkList)
                degerim = resultList[i][2]  # o anki o indexe ait best deger
                if ortalamaCorrelation >= correlationCoefficent and ortalamaCorrelation > degerim:  # thresholdtan ve bir oncekinden buyukse.
                    resultList[i][1] = point2
                    resultList[i][2] = ortalamaCorrelation
    return resultList  # resultListte indexler ve onlarin esleri olan indexler tutulacak.


def glcmDegerleriDondur(glcmTexturelarim, glcmTexturelarim2):
    dissim = 0
    correlation = 0
    contrast = 0
    energy = 0
    ASM = 0
    dissim = np.sum([(x1 - x2) ** 2 for (x1, x2) in zip(glcmTexturelarim[0], glcmTexturelarim2[0])]) ** 0.5
    correlation = np.sum([(x1 - x2) ** 2 for (x1, x2) in zip(glcmTexturelarim[1], glcmTexturelarim2[1])]) ** 0.5
    contrast = np.sum([(x1 - x2) ** 2 for (x1, x2) in zip(glcmTexturelarim[2], glcmTexturelarim2[2])]) ** 0.5
    energy = np.sum([(x1 - x2) ** 2 for (x1, x2) in zip(glcmTexturelarim[3], glcmTexturelarim2[3])]) ** 0.5
    ASM = np.sum([(x1 - x2) ** 2 for (x1, x2) in zip(glcmTexturelarim[4], glcmTexturelarim2[4])]) ** 0.5

    return (dissim, correlation, contrast, energy, ASM)


def glcmDegerleriDondur_V2(glcmTexturelarim, glcmTexturelarim2):
    homogenityValue = 0
    entropyValue = 0
    energyValue = 0
    for g in range(0, len(glcmTexturelarim)):
        gelenDeger1 = list(glcmTexturelarim[g])
        gelenDeger2 = list(glcmTexturelarim2[g])
        # contrastValue += abs(gelenDeger1[0] - gelenDeger2[0])**2
        homogenityValue += abs(gelenDeger1[0][1] - gelenDeger2[0][1]) ** 2
        entropyValue += abs(gelenDeger1[0][2] - gelenDeger2[0][2]) ** 2
        energyValue += abs(gelenDeger1[0][3] - gelenDeger2[0][3]) ** 2
        # contrastValue = contrastValue / (len(tetrisim.glcmTexturelarim))
        homogenityValue = homogenityValue / (len(glcmTexturelarim))
        entropyValue = entropyValue / (len(glcmTexturelarim))
        energyValue = energyValue / (len(glcmTexturelarim))
    return (homogenityValue, entropyValue, energyValue)


def glcmOlustur(patch):
    glcm = greycomatrix(patch, [1], [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4], symmetric=True, normed=True)
    dissim = greycoprops(glcm, 'dissimilarity')
    correlation = greycoprops(glcm, 'correlation')
    contrast = greycoprops(glcm, 'contrast')
    energy = greycoprops(glcm, 'energy')
    ASM = greycoprops(glcm, 'ASM')
    return (dissim, correlation, contrast, energy, ASM)


def gruplardanBuketleriOlusturVeHesaplamaYap(grupListim, featureListim, thresholdDistance, CorrCoeff, thresholdForGLCM=None):
    resultList = []
    for x in range(1, len(grupListim) - 1):
        try:
            # burada gruplar gelicek. simdi burda indexi 1 almamin nedeni 1 den n-1 e kadar 3 lü bucket olusturcam 1. ve sonuncu icin gerek yok buket olusturup bakmaya
            # 1 buket icin 3 grup alicam ilk olarak 1 oncesi , kendisi , 1 sonrasi olucak o gruplardan gelen kordinatlar featureListimde bulunacak indexlerine gore atilacak.
            birOnceki = grupListim[x - 1]
            kendisi = grupListim[x]
            birSonraki = grupListim[x + 1]
            geciciListim = []
            geciciListim.extend(birOnceki)
            geciciListim.extend(kendisi)
            geciciListim.extend(birSonraki)  # bu sekilde biraz uzun yazicam.
            for gecici in geciciListim:
                point1 = gecici[0]
                point1Index = [featureListim.index(x) for x in featureListim if (x[0][0], x[0][1]) == (point1[0], point1[1])][0]
                karsilastirilcakListim = list(filter(lambda x: (x[0][0], x[0][1]) != (point1[0], point1[1]), geciciListim))
                for kar in karsilastirilcakListim:
                    point2 = kar[0]
                    dist = ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5
                    if dist <= thresholdDistance:
                        continue
                    if thresholdForGLCM is not None:
                        dissim, correlation, contrast, energy, ASM = thresholdForGLCM
                        glcmDegerler = glcmDegerleriDondur_V2(gecici[2][0], kar[2][0])  # 2 de glcmtextler var
                        if not (int(glcmDegerler[0]) <= int(dissim) and int(glcmDegerler[1]) <= int(correlation) and int(glcmDegerler[2]) <= int(
                                contrast) and int(glcmDegerler[3]) <= int(energy)
                                and int(glcmDegerler[4]) <= int(ASM)):
                            continue
                    point2Index = [featureListim.index(x) for x in featureListim if (x[0][0], x[0][1]) == (point2[0], point2[1])][0]
                    farkList = [(x1 - x2) for (x1, x2) in zip(gecici[1][0], kar[1][0])]
                    sifirCount = len(list(filter(lambda x: x == 0, farkList)))
                    # ortCorr2 = np.correlate(gecici[1][0],kar[1][0])
                    # ortalamaCorrelation = np.corrcoef(gecici[1][0],kar[1][0])[0][1]
                    # ortCorr4= pearsonr(gecici[1][0],kar[1][0])
                    ortalamaCorrelation = sifirCount / len(farkList)
                    if ortalamaCorrelation >= CorrCoeff:  # ortalama corr degeri buyuk listeye ekliycem sortluycam en sonuncusunu atıcam
                        featureListim[point1Index][4].append([point2Index,
                                                              ortalamaCorrelation])  # 4.indekste listim var -1 karsilasmamis,0 corr alti, >0 correlation degeri
                        featureListim[point1Index][4].sort(key=lambda x: x[1], reverse=True)
                        featureListim[point1Index][4].pop()  # sortladim son indexi attim.


        except BaseException as e:
            print(" grupListim error - {}".format(str(e)))
            pass
            # yukarida featureListime yerlestirdim Correlation degerlerini, simdi maksimum indexleri esleyecegim.
    for i in range(0, len(featureListim)):
        feature = featureListim[i]
        maxValue = feature[4][0][1]
        maxIndex = feature[4][0][0]
        if maxValue > 0:
            resultList.append([feature[0], featureListim[maxIndex][0], maxValue])
    return resultList
