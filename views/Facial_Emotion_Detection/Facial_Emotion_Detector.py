# def faceDatasetHazirla():
#     imageFiles = []
#     i = 1
#     for root, dirs, files in os.walk('C:/Users/fatih/Desktop/KDEF'):
#         for file in files:
#             print('{}.dosya - {} isleniyorrr'.format(str(i),str(file)))
#             try:
#                 if file.endswith('.JPG'):
#                     filepath = root+'/'+file
#                     angle = file[6]
#                     if angle != 'S':
#                         print('atladik..')
#                         continue
#                     gender = dictGender[file[1]]
#                     emotion = dictEmotion[file[4:6]]
#                     image = cv2.imread(filepath)
#                     features,landmarks = ed.startGenerating(image)
#                     if(len(features) != 8855):
#                         continue
#                     if features is not None:
#                         imageFiles.append((file,gender,emotion,features))
#                         # methods.pickleOlustur('Resources/face_expression_data.txt', imageFiles)
#             except BaseException as e:
#                 print(str(e))
#         if len(imageFiles)>0:
#             methods.pickleOlustur('Resources/face_expression_data.pkl', imageFiles)
#         print('..............................bitti..................')
#
# def NeuralNetwork(feature,datas):
#     x=[]
#     y=[]
#     for data in datas:
#         if len(data[3])!=8855:
#             continue
#         satir=[]
#         for value in data[3]:
#             # for data in value[0]:
#             #     satir.append(data)
#             #value[0].append(value[1])
#             satir.append(value[1])
#         x.append(satir)
#         y.append(dictEmotionValue[data[2]])
#         predictValue =[]
#         for valuem in feature:
#             test = []
#             # for data in valuem[0]:
#             #     test.append(data)
#             test.append(valuem[1])
#             predictValue.extend(test)
#
#
#     clf = MLPClassifier(solver='lbfgs', alpha=1e-5,
#                           hidden_layer_sizes=(100, 50), random_state=1)
#
#     X = [[0.,0.], [1., 1.]]
#     clf.fit(x, y)
#     methods.pickleOlustur('Resources/face_expression_data_trained.pkl', clf,1)
#     result = clf.predict([predictValue])
#     print(result)
#     print('tamam')

import views.Methods as methods
import views.Facial_Emotion_Detection.EmoDetect as ed
import cv2

class Facial_Emotion_Detector:
    def __init__(self):
        self.dictEmotion = {'AF': 'Afraid', 'AN': 'Angry', 'DI': 'Disgusted', 'HA': 'Happy', 'NE': 'neutral', 'SA': 'sad', 'SU': 'surprised'}
        self.dictEmotionValue = {'Afraid': 1000, 'Angry': 2000, 'Disgusted': 3000, 'Happy': 4000, 'neutral': 5000, 'sad': 6000, 'surprised': 7000}
        self.predictValue =[]
        self.clf = methods.pickleYukle('Resources/face_expression_data_trained.pkl', 1)

    def predictImage(self,path):
        try:
            image = cv2.imread(path)
            height, width, channels = image.shape
            oranHeight, oranWidth = 1,1
            if height>300:
              oranHeight = height/300
            if width>300:
                oranWidth = width/300
            height = height /oranHeight
            width = width / oranWidth
            imageReturn = image.copy()
            feature, landmarks = ed.startGenerating(image)
            for x,y in landmarks:
                cv2.circle(imageReturn, (x, y), 5, (0, 255, 0), -1)
            for valuem in feature:
                test = []
                test.append(valuem[1])
                self.predictValue.extend(test)
            result=self.clf.predict([self.predictValue])
            imageReturn = cv2.resize(imageReturn, (int(width), int(height)), interpolation=cv2.INTER_CUBIC)
            if result is not None:
                emotion = [key for key, value in self.dictEmotionValue.items() if value == result]
                return emotion[0],imageReturn
            return None
        except BaseException as e:
            print(str(e))
            return None
