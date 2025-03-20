import cv2
import numpy as np
from visual_detection import detect_mines
from thermal_detection import detect_hotspots

thermal_image = "thermal.jpg"
hotspot_image, centers = detect_hotspots(thermal_image)

# Save and display the output
cv2.imwrite("hotspot_detected.jpg", hotspot_image)

visual_path = 'visual.jpg'
visual_img = cv2.imread(visual_path, 0)
template_path = 'template.jpg'

visual_img = cv2.resize(visual_img, None, fx=.6, fy=.6)
detected_img = detect_mines(visual_img, template_path)
