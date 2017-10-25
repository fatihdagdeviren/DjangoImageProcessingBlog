import dlib
import math, itertools

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("Resources/shape_predictor_68_face_landmarks.dat")
faceFeature = None
dataset = []
# Letter 5 & 6
dictEmotion = {'AF': 'Afraid', 'AN': 'Angry', 'DI': 'Disgusted','HA':'Happy','NE':'neutral','SA':'sad','SU':'surprised'}
# Letter 2
dictGender = {'F':'female','M':'male'}

def findRatio(points):
    ''' Function to find ratios '''

    x = [0] * 4
    y = [0] * 4
    for i in range(4):
        x[i] = points[(2 * i)]
        y[i] = points[(2 * i) + 1]

    dist1 = math.sqrt((x[0] - x[1]) ** 2 + (y[0] - y[1]) ** 2)
    dist2 = math.sqrt((x[2] - x[3]) ** 2 + (y[2] - y[3]) ** 2)
    ratio = dist1 / dist2

    return ratio

def generateFeatures(landmarkCoordinates):
    ''' Function to generate features '''
    # len(landmarkCoordinates)
    keyPoints = [18, 22, 23, 27, 37, 40, 43, 46, 28, 32, 34, 36, 5, 9, 13, 49, 55, 52, 58,61,63,65,67]
    combinations = itertools.combinations(keyPoints, 4)
    features = []
    for combination in combinations:
        try:
            ilkNokta = landmarkCoordinates[combination[0]]
            ikinciNokta = landmarkCoordinates[combination[1]]
            ucuncuNokta = landmarkCoordinates[combination[2]]
            dorduncuNokta = landmarkCoordinates[combination[3]]
            points = [ilkNokta[0], ilkNokta[1], ikinciNokta[0], ikinciNokta[1]
                        , ucuncuNokta[0], ucuncuNokta[1], dorduncuNokta[0], dorduncuNokta[1]]
            features.append((combination,findRatio(points)))
        except BaseException as e:
            print(str(e))
    return features

def startGenerating(img):
    # img = io.imread(filename)
    #img = cv2.imread(filename)
    dets = detector(img, 1)
    for k, d in enumerate(dets):
        shape = predictor(img, d)
        landmarks = []
        for i in range(68):
            landmarks.append((shape.part(i).x,shape.part(i).y))
        features = generateFeatures(landmarks)
        return features,landmarks




