import cv2
import numpy as np

def apply_translation(img, tx, ty):
    """Translate the image by tx pixels horizontally and ty pixels vertically."""
    rows, cols = img.shape[:2]
    M = np.float32([[1, 0, tx], [0, 1, ty]])  # Translation matrix
    translated_img = cv2.warpAffine(img, M, (cols, rows))
    return translated_img

def apply_rotation(img, angle, center=None):
    """Rotate the image by a given angle (in degrees) around the center."""
    rows, cols = img.shape[:2]
    if center is None:
        center = (cols // 2, rows // 2)  # Default center is the image center
    M = cv2.getRotationMatrix2D(center, angle, 1)  # Rotation matrix
    rotated_img = cv2.warpAffine(img, M, (cols, rows))
    return rotated_img

def apply_scaling(img, scale_x, scale_y):
    """Scale the image by scale_x in the horizontal direction and scale_y in the vertical direction."""
    rows, cols = img.shape[:2]
    scaled_img = cv2.resize(img, (int(cols * scale_x), int(rows * scale_y)))
    return scaled_img

def manual_alignment(color, depth, thermal):
    # Load images
    visual_img = cv2.imread(color)
    depth_img = cv2.imread(depth,)
    thermal_img = cv2.imread(thermal)

    thermal_img = thermal_img[440:1290, 490:1684] #crop out the key
    visual_img = visual_img[90:1080, 430:1920]
    depth_img = depth_img[0:160, 0:220]
#230, 23
    # Manually apply transformations to both images
    # Example: translation of 50 pixels in x and 30 pixels in y for the thermal image
    #thermal_img = apply_translation(thermal_img, tx=200, ty=0)
    
    # Example: rotating the visual image by 45 degrees
    #rotated_visual = apply_rotation(visual_img, angle=45)
    
    # Example: scaling the thermal image by 0.8 in both directions
    depth_img = apply_scaling(depth_img, scale_x=1500/depth_img.shape[1], scale_y=1000/depth_img.shape[0])
    visual_img = apply_scaling(visual_img, scale_x=1500/visual_img.shape[1], scale_y=1000/visual_img.shape[0])
    thermal_img = apply_scaling(thermal_img, scale_x=1500/thermal_img.shape[1], scale_y=1000/thermal_img.shape[0])

    # Save the transformed images
    #cv2.imwrite('translated_thermal.jpg', translated_thermal)
    cv2.imwrite('depth.jpg', depth_img)
    cv2.imwrite('visual.jpg', visual_img)
    cv2.imwrite('thermal.jpg', thermal_img)

    # Display the transformed images
    #cv2.imshow('Translated Thermal Image', translated_thermal)
    #cv2.imshow('Rotated Visual Image', rotated_visual)
    #cv2.imshow('Scaled Thermal Image', visual_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example usage
manual_alignment('./data/color.png', './data/depth.png', './data/thermal.png')
