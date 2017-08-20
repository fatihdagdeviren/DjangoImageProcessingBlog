class Feature(object):
    """description of class"""
    def __init__(self,pointx,pointy,patchValues=None):
        self.pointX = pointx
        self.pointY = pointy
        self.patchData = patchValues
        self.featureDictionary = {}
        self.featureDictionary_binsize = 0    
        self.otherFeature = None
        self.kontrolText = ''
        self.vektorData = []
        self.glcmTexturelarim = []

    def setOtherFeature(self,otherFeaturem):
        self.otherFeature = otherFeaturem
        

class Feature_PointsAndValues():
    """description of class"""
    def __init__(self,euclidValue,*tupum):
        self.pointX = tupum[0][0]
        self.pointY = tupum[0][1]
        self.featureDictionary_EuclidValue = euclidValue # DictionaryListi yapicam bunu guzel olucak.