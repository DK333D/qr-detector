import argparse
import cv2
from qr_detector import QrDetector


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

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        targets = detector.detect(frame)

        for x, y, r, data in targets:
            cv2.circle(frame, (x, y), r, (0, 0, 255), 4)
            cv2.putText(frame, data, (x - r, y - r - 4), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
