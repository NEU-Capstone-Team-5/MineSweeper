import cv2
import numpy as np

def detect_mines(visual_img, template_path):
    methods = [cv2.TM_CCOEFF_NORMED, cv2.TM_CCORR,
               cv2.TM_CCORR_NORMED, cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]
    
    template = cv2.imread(template_path, 0) # what the mine looks like
    template = cv2.resize(template, None, fx=.6, fy=.6)
    obj_height, obj_width = template.shape

    for method in methods:
        img2 = visual_img.copy() # dont want to draw on og image

        result = cv2.matchTemplate(img2, template, method)
        
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            location = min_loc
        else:
            location = max_loc

        bottom_right = (location[0] + obj_width, location[1] + obj_height)    
        cv2.rectangle(img2, location, bottom_right, 255, 5)
        cv2.imshow('Match', img2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    # File paths
    visual_path = 'visual.jpg'
    visual_img = cv2.imread(visual_path, 0)
    template_path = 'template.jpg'

    visual_img = cv2.resize(visual_img, None, fx=.6, fy=.6)
    detected_img = detect_mines(visual_img, template_path)

if __name__ == '__main__':
    main()
