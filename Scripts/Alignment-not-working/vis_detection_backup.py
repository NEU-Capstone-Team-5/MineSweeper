import cv2
import numpy as np

def detect_mines(visual_img, template_path):
    # Apply Gaussian blur to reduce noise
    # blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # Perform adaptive thresholding for segmentation
    # _, binary_img = cv2.threshold(blurred_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Find contours of potential mines
    # contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    methods = [cv2.TM_CCOEFF, cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,
               cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]
    
    template = cv2.imread(template_path, 0) # what the mine looks like
    template = cv2.resize(template, None, fx=.6, fy=.6)
    obj_height, obj_width = template.shape

    for method in methods:
        img2 = visual_img.copy() # dont want to draw on og image

        result = cv2.matchTemplate(img2, template, method)

        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            locations = np.where(result <= .4) 
        else:
            locations = np.where(result >= .6)

        for y, x in zip(*locations):
            bottom_right = (x + obj_width, y + obj_height)    
            cv2.rectangle(img2, (x, y), bottom_right, 255, 5)
        cv2.imshow(f'Match - Method {method}', img2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    # # Draw contours on the fused image
    # output_img = fused_img.copy()
    # for contour in contours:
    #     if cv2.contourArea(contour) > 1000:  # Filter small detections
    #         x, y, w, h = cv2.boundingRect(contour)
    #         cv2.rectangle(output_img, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # return output_img

def main():
    # File paths
    visual_path = 'visual.jpg'
    visual_img = cv2.imread(visual_path, 0)
    template_path = 'template.jpg'

    #fused_img = cv2.imread('./visual.jpg', 0)
    visual_img = cv2.resize(visual_img, None, fx=.6, fy=.6)
    detected_img = detect_mines(visual_img, template_path)

    # # Save and display results
    # cv2.imwrite('fused_image.jpg', fused_img)
    # cv2.imwrite('detected_mines.jpg', detected_img)

    # cv2.imshow('Fused Image', fused_img)
    # cv2.imshow('Detected Mines', detected_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
