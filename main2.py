import argparse
import cv2
from qr_detector import QrDetector

camera_id = 0
delay = 1
window_name = 'OpenCV QR Code'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', default=0, nargs='?', type=str)
    args = parser.parse_args()

    try:
        args.input = int(args.input)
    except ValueError:
        pass

    detector = QrDetector()
    cap = cv2.VideoCapture(args.input)
    calibrate_str_old="" #for calibration

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        window_center_coordinates=[frame.shape[1]/2,frame.shape[0]/2]
        targets = detector.detect(frame)
        is_success=False #na razie nie potrzebne
        camera_mode="front"

        right="RIGHT "
        left="LEFT "
        top="TOP"
        bottom="BOTTOM"

        if(camera_mode=="front"):
            right="LEFT"
            left="RIGHT "

        for x, y, r, _ in targets:

            object_area=4*r**2
            window_area=frame.shape[0]*frame.shape[0]
            coverage=str(object_area/window_area)
            cv2.circle(frame, (x, y), r, (0, 0, 255), 4)
            cv2.putText(frame, str(x)+" "+str(y), (x-30, y - r - 4), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
            cv2.putText(frame, coverage, (x , y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 4)
            # cv2.putText(frame, "TOP", (x-24 , y-r-2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 4)
            # cv2.putText(frame, "RIGHT", (x+r+2 , y+12), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 4)
            # cv2.putText(frame, "LEFT", (x-r-78 , y+12), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 4)
            # cv2.putText(frame, "BOTTOM", (x-50 , y+r+28), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4)

            # frame = cv2.circle(frame, (x, y-r), 4, (255, 0, 0), -1)
            # frame = cv2.circle(frame, (x+r, y), 4, (255, 0, 255), -1)
            # frame = cv2.circle(frame, (x-r, y), 4, (0, 255, 255), -1)
            # frame = cv2.circle(frame, (x, y+r), 4, (0, 255, 0), -1)

            # czy ma być granica błędu?
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
            if success=="HORIZONTAL_CENTER VERTICAL_CENTER" and float(coverage)>0.75:
                print("SUCCESS! SHOOT! x=", x, " y=", y, "coverage=", coverage)
                success=True
                return
            else:
                calibrate_str+=success            
                # czy ma się wyświetlać cały czas czy tylko kiedy jest potrzebna kalibracja
                if(calibrate_str != calibrate_str_old and success!=""):
                    print("Frame x: ",frame.shape[1]," y: ",frame.shape[0],calibrate_str)
                    print(success, " ", x, " ", y)# print(data)
            calibrate_str_old=calibrate_str

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
