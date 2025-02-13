import cv2
import numpy as np
import os


def getPreviewRGB(preview: np.ndarray, confidence: np.ndarray, confidence_value: int = 30) -> np.ndarray:
    preview = np.nan_to_num(preview)
    preview[confidence < confidence_value] = (0, 0, 0)
    return preview


def process_data(file_path: str):
    """Process a single NPZ file, apply image processing, and save the result."""
    # Load the saved data from the .npz file
    data = np.load(file_path)
    depth_buf = data['depth']
    confidence_buf = data['confidence']
    print(f"Data loaded from: {file_path}")

    # Apply depth data normalization and color map
    r = 1000  # Range value; adjust as needed for your camera setup
    result_image = (depth_buf * (255.0 / r)).astype(np.uint8)
    result_image = cv2.applyColorMap(result_image, cv2.COLORMAP_RAINBOW)
    result_image = getPreviewRGB(result_image, confidence_buf)

    # Get the timestamp for filename
    timestamp = file_path.split('_')[-1].split('.')[0]

    # Add timestamp to image
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    thickness = 1
    color = (255, 255, 255)
    text_size = cv2.getTextSize(timestamp, font, font_scale, thickness)[0]
    text_width, text_height = text_size
    bottom_right = (result_image.shape[1] - text_width - 10, result_image.shape[0] - 10)
    cv2.putText(result_image, timestamp, bottom_right, font, font_scale, color, thickness, cv2.LINE_AA)

    # Save the processed image
    save_path = f"depthImage/depth_image.png"
    cv2.imwrite(save_path, result_image)
    print(f"Processed image saved as {save_path}")

    # Delete the .npz file after processing
    os.remove(file_path)
    print(f"Deleted {file_path}")


def main():
    # Folder containing the .npz files
    folder_path = 'depthImage'
    
    # Iterate through all .npz files in the folder
    for npz_file in os.listdir(folder_path):
        if npz_file.endswith('.npz'):
            # Full file path
            file_path = os.path.join(folder_path, npz_file)
            
            # Process the file and delete after saving the image
            process_data(file_path)


if __name__ == "__main__":
    main()

