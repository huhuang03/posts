import cv2

img = cv2.imread('Lenna.jpg')  # Reads a Gray-scale image
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite("Lenna_gray.jpg", gray)
cv2.imshow("gray", gray)
cv2.waitKey(0)
cv2.destroyAllWindows()

