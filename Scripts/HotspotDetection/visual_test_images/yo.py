import os
import cv2

def resize_images(folder_path, output_folder, width=24, height=24):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    
    for file in files:
        img_path = os.path.join(folder_path, file)
        img = cv2.imread(img_path)

        if img is None:
            print(f"Skipping {file}, unable to read image.")
            continue

        resized_img = cv2.resize(img, (width, height))

        output_path = os.path.join(output_folder, file)
        cv2.imwrite(output_path, resized_img)

        print(f"Resized {file} -> {output_path}")

input_folder = "positives2"  # Replace with your actual folder path
output_folder = "positives"  # Replace with your desired output folder
resize_images(input_folder, output_folder)

