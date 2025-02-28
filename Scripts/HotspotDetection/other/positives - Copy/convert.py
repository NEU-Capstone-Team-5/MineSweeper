import cv2

# Convert an image to grayscale
img = cv2.imread("pos5.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite("pos5.jpg", gray)
