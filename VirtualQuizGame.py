import time
import cv2
import csv
from HandTrackingModule import HandDetector
import Utils
import os

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4,720)
detector = HandDetector(detectionCon=0.8)

class Question():
    def __init__(self, data):
        self.question = data[0]
        self.choice1 = data[1]
        self.choice2 = data[2]
        self.choice3 = data[3]
        self.choice4 = data[4]
        self.answer = int(data[5])

        self.userAns = None

    def update(self, cursor, bboxs):
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                self.userAns = x + 1
                cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), cv2.FILLED)


#import csv data
pathCSV = os.path.dirname(os.path.abspath(__file__)) + "\\questions.csv"
with open(pathCSV,newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]

#Create object for each Question
qList = []
for q in dataAll:
    qList.append(Question(q))

qNo = 0
qTotal = len(dataAll)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    hands, img = detector.findHands(img)
    lmList , bboxInfo = detector.findPosition(img, draw=False) #findposition return lmList[id, x, y]

    if qNo < qTotal:
        mcq = qList[qNo]

        img, bbox = Utils.putTextRect(img, mcq.question, [100,100], 2, 2, offset=50, border=2)

        img, bbox1 = Utils.putTextRect(img, mcq.choice1, [100,300], 2, 2, offset=50, border=2)
        img, bbox2 = Utils.putTextRect(img, mcq.choice2, [450,300], 2, 2, offset=50, border=2)
        img, bbox3 = Utils.putTextRect(img, mcq.choice3, [100,450], 2, 2, offset=50, border=2)
        img, bbox4 = Utils.putTextRect(img, mcq.choice4, [450,450], 2, 2, offset=50, border=2)

        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8]
            
            length, info = detector.findDistance(lmList[4], lmList[8])
            
            print(length)
            if length < 40:
                print("clicked")
                mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4])
                print(mcq.userAns)
                if mcq.userAns is not None:
                    time.sleep(0.3)
                    qNo += 1
    else:
        score = 0
        for mcq in qList:
            if mcq.answer == mcq.userAns:
                score += 1
        
        score = round((score / qTotal)*100,2)
        img, _ = Utils.putTextRect(img, "Quiz Completed", [250,300], 2, 2, offset=50, border=5)
        img, _ = Utils.putTextRect(img, f'Your score: {score}%', [700,300], 2, 2, offset=50, border=5)
        
    #Draw progress bar
    barValue = 150 + (950//qTotal)*qNo
    cv2.rectangle(img, (150, 600), (barValue, 650), (0,255,0), cv2.FILLED)
    cv2.rectangle(img, (150, 600), (1100, 650), (255, 0, 255), 5)
    img, _ = Utils.putTextRect(img, f'{round((qNo/qTotal)*100)}%', [1130,635], 2, 2, offset=16) #offset is margin

    cv2.imshow("Toeic", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        break

