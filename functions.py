
import cv2
from qr_detector import QrDetector
import numpy as np
import math
import time

def calculateAreaAndFindMiddlePoint(points):
    # a = [int(val) for val in points[0]]
    # print(a)
    a = points[0].astype(int)
    b = points[(1) % 4].astype(int)
    c = points[(2) % 4].astype(int)
    d = points[(3) % 4].astype(int)

    # uśrednianie punktów z kilku iteracji
    # ab=np.linalg.norm(a[0]-b[0])
    ab=np.linalg.norm([a[0]-b[0],a[1]-b[1]])
    bc=np.linalg.norm([b[0]-c[0],b[1]-c[1]])
    cd=np.linalg.norm([c[0]-d[0],d[0]-a[0]])
    da=np.linalg.norm([d[0]-a[0],d[0]-a[0]])
    p=(ab+bc+cd+da)/2
    area=math.sqrt(abs((p-ab)*(p-bc)*(p-cd)*(p-da)))

    middle_x=(a[0]+b[0]+c[0]+d[0])/4
    middle_y=(a[1]+b[1]+c[1]+d[1])/4
    # print('Area: ',area)
    return area, [middle_x, middle_y]
# returns if object detected, centered and close
def detectAndMark(cv2, frame,detector):
    try: 
        data, points, _ = detector.detectAndDecode(frame)
    except:
        print("detectAndMark(...) exception!!!")
        return False, ""
    if data=="":
        return False, data
    # print(data)
    window_center_coordinates=[round(frame.shape[1]/2),round(frame.shape[0]/2)]
    targets = detector.detect(frame)
    camera_mode="front"

    right="RIGHT "
    left="LEFT "
    top="TOP "
    bottom="BOTTOM "

    if(camera_mode=="front"):
        right="LEFT "
        left="RIGHT "

    x=0
    y=0
    calibrate_str_old="" #for calibration

    if points is not None and points[0] is not None:
        points = points[0]
        for i in range(len(points)):
            pt1 = [int(val) for val in points[i]]
            pt2 = [int(val) for val in points[(i + 1) % 4]]
            area, [x, y]=calculateAreaAndFindMiddlePoint(points[0:4])
            # print(x," ",y)
            coverage=area/frame.shape[0]/frame.shape[1]
            # print('Coverage: ',coverage)
            cv2.line(frame, pt1, pt2, color=(255, 0, 0), thickness=2)
            epsilon=20

            calibrate_str="Calibrate: "
            success=""

            if x-window_center_coordinates[0]>epsilon:
                calibrate_str+=(left)
            elif x-window_center_coordinates[0]<-epsilon:
                calibrate_str+=(right)
            else:
                success+="HORIZONTAL_CENTER "

            if y-window_center_coordinates[1]>epsilon:
                calibrate_str+=(top)
            elif y-window_center_coordinates[1]<-epsilon:
                calibrate_str+=(bottom)
            else:
                success+="VERTICAL_CENTER"

            # coverage może być większe niż 1 przez kwadratową ramkę window_area
            if success=="HORIZONTAL_CENTER VERTICAL_CENTER" and float(coverage)>0.25:
                # print("SUCCESS! SHOOT! x=", x, " y=", y, "coverage=", coverage)
                is_success=True
                cv2.putText(frame, "X", (round(window_center_coordinates[0]),round(window_center_coordinates[1])), cv2.FONT_HERSHEY_SIMPLEX, 6, (0, 0, 255), 1)

                return is_success, data
                # return
            else:
                calibrate_str+="Success: "+success            
                # czy ma się wyświetlać cały czas czy tylko kiedy jest potrzebna kalibracja
                if(calibrate_str != calibrate_str_old and success!=""):
                    # print("Frame x: ",frame.shape[1]," y: ",frame.shape[0],calibrate_str)
                    # print(success, " ", x, " ", y)# print(data)
                    pass
                cv2.putText(frame, calibrate_str, (16 , 16), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

            calibrate_str_old=calibrate_str
    return False, data

# returns if object detected, centered and close
def detectAndMarkCircle(cv2, frame,detector):
    targets = detector.detect(frame)

    for x, y, r, data in targets:
        cv2.circle(frame, (x, y), r, (0, 0, 255), 4)
        cv2.putText(frame, data, (x - r, y - r - 4), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)


def get_output(codec , fps,out=None, filename=None):
    if filename is None:
        filename='RecordNone.avi'
    #Specify the path and name of the video file as well as the encoding, fps and resolution
    if out:
        out.release()
    return cv2.VideoWriter(filename, codec , fps, (640,480))
# fps dependent on camera fps
def get_fps(cap):
    (major_ver, _, _) = (cv2.__version__).split('.')
    if int(major_ver) < 3:
        fps1 = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        print ("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps1))
    else:
        fps1 = cap.get(cv2.CAP_PROP_FPS)
        print ("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps1))
    return fps1

def generateVideoName(number, postfix=""):
    hour, minute = map(int, time.strftime("%H %M").split())
    return "success-video_{0}_{1}_{2}{3}.avi".format(number,hour,minute, postfix)

