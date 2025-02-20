from depth_hotspot import extract_depth_values
from thermal_hotspot import detect_hotspots
import cv2
import numpy as np

thermal_image = "1.png"
hotspot_image, thermal_hotspot_centers = detect_hotspots(thermal_image, threshold=200)

# Save and display the thermal hotspots
cv2.imwrite("hotspot_detected.jpg", hotspot_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

depth_image_path = "depth_test.png"  # Replace with actual depth image

depth_to_check = []
imageT = cv2.imread(thermal_image)
depth_image = cv2.imread(depth_image_path)
wT, hT = imageT.shape[1], imageT.shape[0]
wD, hD = depth_image.shape[1], depth_image.shape[0]
width_conversion, height_conversion = wD/wT, hD/hT

# convert coordinates from the thermal image size to depth image size
for x, y in thermal_hotspot_centers:
    depth_to_check.append((int(x*width_conversion), int(y*height_conversion)))

depth_results = extract_depth_values(depth_image_path, depth_to_check) # check the hotspots from the thermal in the depth

# Print extracted depth values
for point, depth in depth_results.items():
    print(f"Depth at {point}: {depth} units")

#avg depth
# Remove invalid values (e.g., zero depth)
valid_depth = depth_image[depth_image > 0]  # Exclude zero values

# Compute average depth
average_depth = np.mean(valid_depth) if valid_depth.size > 0 else 0

print(f"Average Depth: {average_depth:.2f}")