import cv2

class Diabetic_Retinopathy():
    def __init__(self,path):
        self.imagePath = path
        self.image = cv2.imread(path)

    def findExudates(self,thresholdValue,medianFilterDimension):
        if self.image is None:
            return None
        grayImage = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        grayImage  = cv2.medianBlur(grayImage,medianFilterDimension)
        # create a CLAHE object (Arguments are optional).
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        claheImage = clahe.apply(grayImage)
        #morphological operations.(closing yapılıyor  burada.)
        claheImage = cv2.dilate(claheImage, None, iterations=1)
        claheImage = cv2.erode(claheImage, None, iterations=1)
        # Set threshold and maxValue
        maxValue = 255
        # Basic threshold example
        ret, thresholdedImage = cv2.threshold(claheImage, thresholdValue, maxValue, cv2.THRESH_BINARY)
        return thresholdedImage

class Age_Related_Macular_Degeneration:
    def __init__(self,path):
        self.imagePath = path
        self.image = cv2.imread(self.imagePath)

    def findDrusens(self,thresholdValue):
        b, g, r = cv2.split(self.image)
        #green component kullanılacak burada.
        # create a CLAHE object (Arguments are optional).
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        claheImage = clahe.apply(g)
        maxValue = 255
        # Basic threshold example
        ret, thresholdedImage = cv2.threshold(claheImage, thresholdValue, maxValue, cv2.THRESH_BINARY)
        return thresholdedImage