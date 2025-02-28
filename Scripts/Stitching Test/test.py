import cv2
import glob

# Load all images from a folder
image_files = sorted(glob.glob("pics/*.png"))  # Adjust path as needed
images = [cv2.imread(img) for img in image_files]

# Initialize OpenCV’s Stitcher
stitcher = cv2.Stitcher_create()

# Perform stitching
status, stitched = stitcher.stitch(images)

if status == cv2.STITCHER_OK:
    cv2.imshow("Stitched Image", stitched)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite("stitched_output.jpg", stitched)  # Save result
else:
    print("Image stitching failed. Try improving image overlap and order. Error: "+status)
