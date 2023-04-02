import argparse
import cv2
from qr_detector import QrDetector
import functions
import time

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
    
    # zero every timestamp 
    counter=0
    # count to this number before shoot
    counter_treshold=1

    
    timestamp=5
    out=None
    next_time = time.time()
    
    camera_id = 0
    delay = 1
    window_name = 'OpenCV QR Code'
    resolution = (640, 480)

    #chosen experimentally
    fps = 15.0

    # Specify video codec
    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    codec = cv2.VideoWriter_fourcc(*"XVID")

    record_after_aim=False 
    record_after_shoot=False 
    time_to_shoot=5
    #to be able to record properly
    time_to_shoot%=(2*timestamp)
    
    video_name=functions.generateVideoName(0)
    # Array of collected QR codes
    QRcollected=[]

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        detector = cv2.QRCodeDetector()
        is_detected,data_qr=functions.detectAndMark(cv2, frame,detector)
        if data_qr!="":
            counter+=1

        #check if we should shoot
        if is_detected and counter>counter_treshold and data_qr != "" and data_qr not in QRcollected:
            QRcollected.append(data_qr)
            print("Aim")
            video_name=functions.generateVideoName(number=len(QRcollected),postfix="aim")
            print(video_name)
            out = cv2.VideoWriter(video_name, codec, fps, resolution)
            record_after_aim=True

            #change next_time
            next_time=time.time()+2*timestamp

        elif data_qr in QRcollected:
            print("Go on. Element already in collection ")

        if record_after_aim or record_after_shoot:
            out.write(frame)

        #change time and reset counter
        if time.time() > next_time-10+time_to_shoot:
            # next_time += timestamp
            counter=0
            if record_after_aim:
                out.release()
                video_name=functions.generateVideoName(number=len(QRcollected),postfix="aftershoot")
                out = functions.get_output(codec, fps, out, video_name)
                record_after_aim=False
                record_after_shoot=True
                

        if time.time() > next_time:
            next_time += 2*timestamp
            if record_after_shoot:
                out.release()
                record_after_shoot=False

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) == ord('q'):
            break
        if cv2.waitKey(3) == 27:
            break
    if out:
        out.release()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
