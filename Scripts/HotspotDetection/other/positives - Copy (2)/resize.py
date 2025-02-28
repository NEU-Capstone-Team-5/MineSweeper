import cv2

image = cv2.imread('path/to/your/image.jpg')
resized_image = cv2.resize(image, (24, 24))
cv2.imwrite('path/to/save/resized_image_aspect_ratio.jpg', resized_image)