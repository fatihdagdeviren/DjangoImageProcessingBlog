
import numpy as np



def shift(seq, n):
    n = n % len(seq)
    return seq[n:] + seq[:n]


def blockshaped(arr, nrows, ncols):
    """
    Return an array of shape (n, nrows, ncols) where
    n * nrows * ncols = arr.size

    If arr is a 2D array, the returned array should look like n subblocks with
    each subblock preserving the "physical" layout of arr.
    """
    h, w = arr.shape
    return (arr.reshape(h//nrows, nrows, -1, ncols)
               .swapaxes(1,2))

# Bolgeleri Olustur metodu ilk olarak patch uzerinde 3x3 alanlar olusturuyor.
# Daha sonra 3x3 luk olusan array kadar yeni bir 2d array olusturuyorum.15x15 lik icin 5x5 kadar 3x3 alan var
# Daha sonra 5x5 alanı ve icerisindeki (index degerleri var) katmansal yapıya dahil ediyorum. Disaridan iceriye dogru.
def bolgeleriOlustur(featureListim,thresholdForltp,komsulukListesiSayisi,threholdForGLCM=None):
    koorListim = []
    ltpCodeListim = []
    for feature in featureListim:
        try:
            feature.vektorData = []
            blocks = blockshaped(feature.patchData,3,3)
            height = len(blocks)
            width = len(blocks[0])
            indexArr = np.arange(height**2).reshape((height,width))
            katmanList = []
            index = int((height+1)/2)
            for i in range(0,index): # karesel alan zaten
                katmanList.extend(indexArr[i,i:height-1-i]) #ustKisim
                katmanList.extend(indexArr[i:height-1- i, height - 1 - i])  # sag Kisim
                katmanList.extend(indexArr[height - 1 - i, i:height - i][::-1])  # tersten burada,Alt Kisim
                katmanList.extend(indexArr[i+1:height-1-i, i][::-1]) #solKisim

            #LTP kodunu olusturup ekliyorum buraya.
            [feature.vektorData.extend(ltpStringGetir(blocks[x//height,x%height],thresholdForltp)) for x in katmanList]

            koorListim.append((feature.pointX, feature.pointY))
            ltpCodeListim.append(feature.vektorData)
        except BaseException as e: 
            print(" feature olusturuken hata - {}" ,str(e))
            pass
    return koorListim,ltpCodeListim

# [-1,1] araligindan olusan vektor getiren fonksiyon.
def ltpStringGetir(datam,thresholdForltp):        
    yeniList =[]
    yeniList.append(datam[0][0]) #ilk sirada 0,0 indexi
    yeniList.append(datam[0][1])
    yeniList.append(datam[0][2])
    yeniList.append(datam[1][2])
    yeniList.append(datam[2][2])
    yeniList.append(datam[2][1])
    yeniList.append(datam[2][0])
    yeniList.append(datam[1][0]) #1,1 merkez almayacagim.
    merkezim = datam[2][2]
    merkez_maksNerde = np.argmax(yeniList)
    if merkez_maksNerde > 0: #kaykil bakam
        temp_d = shift(yeniList,merkez_maksNerde)
        datam = temp_d
    else:
        datam = yeniList
    lbpVektor_merkez=[]
    for lbp in datam:
        if lbp<=merkezim-thresholdForltp:
           lbpVektor_merkez.append(-1)
        elif merkezim-thresholdForltp<lbp<merkezim+thresholdForltp:
            lbpVektor_merkez.append(0)
        else:
            lbpVektor_merkez.append(1)
    upperPattern = [0 if x <= 0  else 1 for x in lbpVektor_merkez]
    lowerPattern = [1 if x < 0  else 0 for x in lbpVektor_merkez]
    upperResult = 0
    lowerResult = 0
    for index in range(0,len(upperPattern)): # tek satir yerine range daha iyi 0 ve 1  lerde index karisiyor.
        upperResult += (2**index)*upperPattern[index]
        lowerResult += (2 ** index) * lowerPattern[index]
    return upperResult,lowerResult


def bolgeleriEslestir(koordinatListim,ltpCodeListim,thresholdDistance,thresholdSimilarity):
    # buraya liste iceren liste gondericem bu sekilde ilerde hizlandiricam ve threadli calisma yapabilmeyi umuyorum.
    resultList= [] # -1 iceren list olusturuyorum
    for i in range(0,len(koordinatListim)):
        point1 = koordinatListim[i]
        distanceCheckIndexList = [koordinatListim.index(point2) for point2 in koordinatListim if ((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)**0.5>= thresholdDistance ]
        #distanceCheckIndexList icerisinde uzaklik olarak thresholdtan buyuk olan indexler olmali.
        distanceList = [(i,x,np.corrcoef(np.array(ltpCodeListim[i]),np.array(ltpCodeListim[x]))[0, 1])  for x in distanceCheckIndexList]
                                      #if sum(el1 == el2 for el1, el2 in zip(ltpCodeListim[i], ltpCodeListim[x]))/len(ltpCodeListim[i])>=thresholdSimilarity]

        distanceList = list(filter(lambda  x: x[2]>=thresholdSimilarity,distanceList)) #thresholdtan buyuk olanlar, coklu eslesmeye izin veriyorum
        #inverseHammingDistanceList.sort(key=lambda x: x[1],reverse=True)
        if len(distanceList)>0:
            resultList.extend(distanceList)
    return resultList # resultListte indexler ve onlarin esleri olan indexler tutulacak.





def bolgeleriEslestir_thread(koordinatListim,ltpCodeListim,thresholdDistance,thresholdSimilarity):
    import itertools
    # buraya liste iceren liste gondericem bu sekilde ilerde hizlandiricam ve threadli calisma yapabilmeyi umuyorum.
    resultList= [] # -1 iceren list olusturuyorum
    crossProductList = list(itertools.product(list(range(0,len(koordinatListim))),list(range(0,len(koordinatListim)))))
    listForThread = list(zip(crossProductList,itertools.repeat(ltpCodeListim)))
    results = list(map(ComputeCorrCoefff, listForThread))
    thresholdtanBuyukOlanlar = [x for x in results if x[2]>= thresholdSimilarity
                                 and  ((koordinatListim[x[0]][0]-koordinatListim[x[1]][0])**2 + (koordinatListim[x[0]][1]-koordinatListim[x[1]][1])**2)**0.5>= thresholdDistance  ]

    if len(thresholdtanBuyukOlanlar)>0:
        resultList.extend(thresholdtanBuyukOlanlar)
    return resultList # resultListte indexler ve onlarin esleri olan indexler tutulacak.


def ComputeCorrCoeff(index,a,b,c,d):
    try:
        return index,np.corrcoef(a,b)[0, 1],c,d
    except:
        return index,0

def ComputeCorrCoefff(listem):
    try:
        #return index[0],index[1],np.corrcoef(listem[index[0]],listem[index[1]])[0, 1]
        return listem[0][0],listem[0][1], np.corrcoef(listem[1][listem[0][0]], listem[1][listem[0][1]])[0, 1]
    except:
        return listem[0][0],listem[0][1],0







       
    
    
      
                             
        
                                 
            



                
