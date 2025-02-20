import cv2
import numpy as np

# Load images
thermal_img = cv2.imread("thermal_test.png", cv2.IMREAD_GRAYSCALE)
depth_img = cv2.imread("depth_test.png", cv2.IMREAD_UNCHANGED)  # 16-bit depth

# Normalize depth image to match 8-bit scale
depth_img_norm = cv2.normalize(depth_img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

# Resize to ensure both images have the same dimensions
thermal_img = cv2.resize(thermal_img, (depth_img_norm.shape[1], depth_img_norm.shape[0]))

# Save normalized depth for visualization
cv2.imwrite("depth_normalized.jpg", depth_img_norm)

# Apply Canny edge detection
edges_thermal = cv2.Canny(thermal_img, 50, 150)
depth_filtered = cv2.bilateralFilter(depth_img_norm, 9, 75, 75)  # Reduces noise but preserves edges
edges_depth = cv2.Canny(depth_filtered, 50, 150)


# Save results
cv2.imwrite("edges_thermal.jpg", edges_thermal)
cv2.imwrite("edges_depth.jpg", edges_depth)

# Display
cv2.imshow("Thermal Edges", edges_thermal)
cv2.imshow("Depth Edges", edges_depth)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Detect ORB features
orb = cv2.ORB_create()
keypoints1, descriptors1 = orb.detectAndCompute(edges_thermal, None)
keypoints2, descriptors2 = orb.detectAndCompute(edges_depth, None)

# Match features using FLANN-based matcher
matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = matcher.match(descriptors1, descriptors2)
matches = sorted(matches, key=lambda x: x.distance)

# Find homography for alignment
src_pts = np.float32([keypoints1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

matrix, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

# Apply transformation
aligned_thermal = cv2.warpPerspective(thermal_img, matrix, (depth_img_norm.shape[1], depth_img_norm.shape[0]))

cv2.imwrite("aligned_thermal.jpg", aligned_thermal)
