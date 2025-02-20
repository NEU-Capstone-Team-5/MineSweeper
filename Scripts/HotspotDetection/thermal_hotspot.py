import cv2
import numpy as np

def detect_hotspots(thermal_image_path, threshold=200):
    """
    Detects hotspots in a thermal image.
    
    :param thermal_image_path: Path to the thermal image.
    :param threshold: Pixel intensity threshold for hotspot detection.
    :return: Processed image with detected hotspots.
    """
    # Load image
    image = cv2.imread(thermal_image_path)
    
    # Convert to grayscale if needed
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding (hotspots will be the brightest areas)
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    # Find contours (hotspot regions)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # save the centers of hotspots
    centers = []

    # Draw bounding boxes around hotspots
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Red boxes

        centers.append((x+(w//2), y+(h//2)))

    #return image, thresh
    return image, centers

# thermal_image = "1.png"
# #hotspot_image, thresholded = detect_hotspots(thermal_image, threshold=200)
# hotspot_image, centers = detect_hotspots(thermal_image, threshold=200)

# # Save and display the output
# cv2.imwrite("hotspot_detected.jpg", hotspot_image)
# cv2.imshow("Hotspots", hotspot_image)
# #cv2.imshow("Thresholded", thresholded)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
