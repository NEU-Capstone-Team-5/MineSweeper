import cv2

# Load the trained classifier
cascade = cv2.CascadeClassifier('haar_training/cascade.xml')

# Load the test image
image = cv2.imread('testpos.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Detect objects
detections = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(24, 24))

# Draw bounding boxes around detected objects
for (x, y, w, h) in detections:
    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

# Show the result
cv2.imshow('Detection', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
