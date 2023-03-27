import argparse
import cv2
from qr_detector import QrDetector
import numpy as np
import math
import time

camera_id = 0
delay = 1
window_name = 'OpenCV QR Code'
# Specify resolution
resolution = (640, 480)
# Specify name of Output file
# filename = "Recording.avi"
    
# Specify frames rate. We can choose any
# value and experiment with it
fps = 60.0

# Specify video codec
# fourcc = cv2.VideoWriter_fourcc(*'MJPG')
codec = cv2.VideoWriter_fourcc(*"XVID")

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
        return
    window_center_coordinates=[frame.shape[1]/2,frame.shape[0]/2]
    targets = detector.detect(frame)
    is_success=False #na razie nie potrzebne
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
            print(x," ",y)
            coverage=area/frame.shape[0]/frame.shape[1]
            print('Coverage: ',coverage)
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
            if success=="HORIZONTAL_CENTER VERTICAL_CENTER" and float(coverage)>0.65:
                print("SUCCESS! SHOOT! x=", x, " y=", y, "coverage=", coverage)
                is_success=True
                return is_success
                # return
            else:
                calibrate_str+="Success: "+success            
                # czy ma się wyświetlać cały czas czy tylko kiedy jest potrzebna kalibracja
                if(calibrate_str != calibrate_str_old and success!=""):
                    print("Frame x: ",frame.shape[1]," y: ",frame.shape[0],calibrate_str)
                    print(success, " ", x, " ", y)# print(data)
                cv2.putText(frame, calibrate_str, (16 , 16), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

            calibrate_str_old=calibrate_str
    return False

def get_output(part,out=None, filename=None):
    if filename is None:
        filename="Record"+str(part) + '.avi'
    #Specify the path and name of the video file as well as the encoding, fps and resolution
    if out:
        out.release()
    return cv2.VideoWriter(filename, codec , fps/4, (640,480))

def main(): 
    timestamp=5
    out=None
    next_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('input', default=0, nargs='?', type=str)
    args = parser.parse_args()

    
    # Creating a VideoWriter object
    out = cv2.VideoWriter("Record0.avi", codec, fps, resolution)
    
    # Create an Empty window
    cv2.namedWindow("Live", cv2.WINDOW_NORMAL)
    
    try:
        args.input = int(args.input)
    except ValueError:
        pass

    # detector = QrDetector()
    detector = cv2.QRCodeDetector()
    cap = cv2.VideoCapture(args.input)
    #Record the current time
    # current_time = time.time()
    part=0
    while True:
        ret, frame = cap.read()

        if not ret:
            break
        

        is_success=detectAndMark(cv2, frame, detector)
        cv2.imshow('Video', frame)

        out.write(frame)


        if time.time() > next_time:
            next_time += timestamp
            out = get_output(part, out)
            part+=1
            part%=2

        # Capture frame-by-frame
        # ret, frame = cap.read() 

        # if ret:
        # out.write(frame)q
            
        if is_success:
        #     # next_time += timestamp
        #     get_output(part, out, filename="Record_last.avi")
        #     part+=1
        #     # part%=2
            cap.release()
            cv2.destroyAllWindows()


        if cv2.waitKey(1) == ord('q'):
            break
 
    # Release the Video writer
    out.release()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
