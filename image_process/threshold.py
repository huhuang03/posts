import cv2
import numpy as np

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('Cannot open camera')
    exit()

ret, frame = cap.read()
threshold = 180
output = np.empty(frame.shape, np.uint8)

h, w, _ = frame.shape
while True:
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = gray_img > threshold
    mask = mask.astype(np.uint8)
    mask *= 255

    cv2.imshow('img', gray_img)
    cv2.imshow('threshold', mask)
    cv2.setWindowTitle('threshold', f'threshold: {threshold}')
    ret, frame = cap.read()

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('+'):
        threshold += 1
    elif key == ord('-'):
        threshold -= 1

cap.release()
cv2.waitKey(0)
cv2.destroyAllWindows()
