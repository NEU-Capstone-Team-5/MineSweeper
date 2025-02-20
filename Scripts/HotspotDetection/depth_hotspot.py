import cv2
import numpy as np

def extract_depth_values(depth_image_path, points=[]):
    """
    Extracts depth values from specific points in a depth image.

    :param depth_image_path: Path to the depth image (16-bit or 32-bit format).
    :param points: List of (x, y) coordinates to extract depth from.
    :return: Dictionary with pixel coordinates and depth values.
    """
    # Load depth image (ensure it's in grayscale mode)
    depth_image = cv2.imread(depth_image_path, cv2.IMREAD_UNCHANGED)

    # Check if image is valid
    if depth_image is None:
        raise ValueError("Error loading depth image!")

    # Convert to grayscale if the image is not single-channel
    if len(depth_image.shape) == 3:
        depth_image = cv2.cvtColor(depth_image, cv2.COLOR_BGR2GRAY)

    # Extract depth values at given points
    depth_values = {}
    for (x, y) in points:
        depth = depth_image[y, x]  # Access pixel (y, x)
        depth_values[(x, y)] = depth

    return depth_values

# # Example usage
# depth_image_path = "depth_test.png"  # Replace with actual depth image
# points_to_check = [(100, 150), (200, 160)]  # Sample pixel coordinates
# depth_results = extract_depth_values(depth_image_path, points_to_check)

# # Print extracted depth values
# for point, depth in depth_results.items():
#     print(f"Depth at {point}: {depth} units")
