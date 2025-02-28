import cv2

# Convert an image to grayscale
img = cv2.imread("neg3.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite("neg3.jpg", gray)
