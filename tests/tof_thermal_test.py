"""
File: tof_thermal_test.py
Author: Alston Liu
Date: 02-10-25
Date Modified: 02-12-25
Description: 
    Tests ToF sensors and thermal cameras by snapping 10 screenshots. Tests uses multiple processes and threads to process the data.
    
    Notes:
    - Please make sure hardware contains at least 4 cores.
    - Thermal images are not interpolated
    - A delay of 1 second between each screenshot

"""
# import libraries here
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO! This is probably because you need superuser privileges.\
          You can achieve this by using 'sudo' to run your script")

# sensor libraries
import adafruit_mlx90640 as thermal_cam
import ArducamDepthCamera as ac
import board
import busio

# data processing 
import matplotlib.pyplot as plt
import numpy as np

# essential libraries
import os
import cv2
import time
from typing import *
from datetime import datetime
from pathlib import Path

# Concurrency Libraries
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed

def collect_thermal_data(mlx, queue):
    """ Collects 10 thermal frames on a separate process

    Args:
        queue (_type_): Reference to the Concurrent Queue to add to the post processing
    """    
    
    # set refresh rate
    mlx.refresh_rate = thermal_cam.RefreshRate.REFRESH_64_HZ
    mlx_shape = (24, 32)
    num_frames = 0
    
    # collect 10 frames
    while num_frames < 10:
        try:
            # Setup frame for storing temperatures
            frame = np.zeros((24 * 32,))
            mlx.getFrame(frame) # Read MLX temperatures into frame var
            data_array = np.reshape(frame, mlx_shape)
            print("Thermal Frame Received")
            
            # timeframe
            now = datetime.now()
            timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
            
            # save data to .npz file
            npz_path = (os.getcwd() + f"/data/thermal/mlx90640_{timestamp}.npz")
            np.savez(npz_path, temperature=data_array)
            
            # package data dictionary
            data = {
                "sensor": "thermal",
                "timestamp": timestamp,
                "path": npz_path
            }
            
            # add data to process queue
            queue.put(data)
            
            # put a delay for package movement
            time.sleep(1) # 1 second
            
            # increase # of frames
            num_frames += 1
        except Exception as e:
            print(f"Error: {e.args}")     

def collect_tof_data(cam, queue):
    """ Collects 10 depth frames on a separate process.

    Args:
        queue (_type_): Reference to the Concurrent Queue to add to the post processing
    """    
    # Setup Depth Camera
    ret = cam.open(ac.Connection.CSI, 0)
    if ret != 0:
        print("Failed to open camera. Error code:", ret)
        return

    ret = cam.start(ac.FrameType.DEPTH)
    if ret != 0:
        print("Failed to start camera. Error code:", ret)
        cam.close()
        return
    
    frame_count = 0
    while frame_count < 10:
        frame = cam.requestFrame(2000)
        print("ToF Frame received")
        if frame is not None and isinstance(frame, ac.DepthData):
            depth_buf = frame.depth_data
            confidence_buf = frame.confidence_data
            
            # Get the timestamp
            now = datetime.now()
            timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
            
            # save data to .npz file
            npz_path = (os.getcwd() + f"/data/depth/tof_{timestamp}.npz")
            np.savez(npz_path, depth=depth_buf, confidence=confidence_buf)
            
            # package data
            data = {
                "sensor": "depth",
                "timestamp": timestamp,
                "path": npz_path
            }
            
            # add to queue
            queue.put(data)
            
            # put a delay for package movement
            time.sleep(1) # 1 second
            
            # release frame
            cam.releaseFrame(frame)
            frame_count += 1
    
    cam.stop()
    cam.close()

def getPreviewRGB(preview: np.ndarray, confidence: np.ndarray, confidence_value: int = 30) -> np.ndarray:
    preview = np.nan_to_num(preview)
    preview[confidence < confidence_value] = (0, 0, 0)
    return preview
    
def process_tof_data(data: Dict):
    """Process a single NPZ file, apply image processing, and save the result."""
    
    # Iterate through all .npz files in the folder
    timestamp =  data["timestamp"]
    folder_path, npz_file = os.path.split(data["path"])
    
    if npz_file.endswith('.npz'):
        # Full file path
        file_path = os.path.join(folder_path, npz_file)
        
        # Process the file and delete after saving the image
        # Load the saved data from the .npz file
        data = np.load(file_path)
        depth_buf = data['depth']
        confidence_buf = data['confidence']
        # print(f"Data loaded from: {file_path}")

        # Apply depth data normalization and color map
        r = 1000  # Range value; adjust as needed for your camera setup
        result_image = (depth_buf * (255.0 / r)).astype(np.uint8)
        result_image = cv2.applyColorMap(result_image, cv2.COLORMAP_RAINBOW)
        result_image = getPreviewRGB(result_image, confidence_buf)

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
        image_path = folder_path + '/../images'
        # Save the processed thermal image
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        
        save_path = os.path.join(image_path, f"depth_{timestamp}.png")
        cv2.imwrite(save_path, result_image)
        # print(f"Processed image saved as {save_path}")

        # Delete the .npz file after processing
        os.remove(file_path)
        # print(f"Deleted {file_path}")

def process_thermal_data(data: Dict):
    """Process thermal data and save the processed image."""
    
    # Iterate through all .npz files in the folder
    timestamp =  data["timestamp"]
    folder_path, npz_file = os.path.split(data["path"])
    
    if npz_file.endswith('.npz'):
        # Full file path
        file_path = os.path.join(folder_path, npz_file)
        
        # Load the saved thermal data from the .npz file
        data = np.load(file_path)
        temperature_data = data['temperature']
        # print(f"Data loaded from: {file_path}")

        # Setup the figure for plotting
        plt.ion()
        fig, ax = plt.subplots(figsize=(12, 7))
        therm1 = ax.imshow(np.zeros(temperature_data.shape), cmap='plasma', vmin=0, vmax=60)
        cbar = fig.colorbar(therm1)
        cbar.set_label('Temperature [$^{\circ}$C]', fontsize=14)

        # Update the thermal image with the data
        therm1.set_data(np.fliplr(temperature_data))  # Flip left to right
        therm1.set_clim(vmin=np.min(temperature_data), vmax=np.max(temperature_data))  # Set bounds
        cbar.update_normal(therm1)

        image_path = folder_path + '/../images'
        # Save the processed thermal image
        if not os.path.exists(image_path):
            os.makedirs(image_path)

        save_path = os.path.join(image_path, f"thermal_image_{timestamp}.png")
        fig.savefig(save_path, dpi=300, facecolor='#FCFCFC', bbox_inches='tight')
        # print(f"Processed thermal image saved as {save_path}")

        # Close the figure to avoid memory issues
        plt.close(fig)

        # Delete the .npz file after processing
        os.remove(file_path)
        # print(f"Deleted {file_path}")

def process_data(queue):
    """ Processes Thermal and Depth Data and converts it into an image using threads

    Args:
        queue (_type_): data packets that needs to be processed
    """    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        
        # Add tasks when queue is not empty
        while True:
            if not queue.empty():
                batch = queue.get()
                # get null batch
                if batch is None:
                    break;
                
                # pushing to either one
                type = batch["sensor"]
                
                # transfer batch to the appropriate function
                if (type == "depth"):
                    futures.append(executor.submit(process_tof_data, batch))
                elif (type == "thermal"):
                    futures.append(executor.submit(process_thermal_data, batch))
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing data: {e}")
                
def main():
    # Create device objects 
    # Setup Thermal Camera
    i2c = busio.I2C(board.SCL, board.SDA)
    mlx = thermal_cam.MLX90640(i2c)
    
    # Setup ToF Camera
    cam = ac.ArducamCamera()
    
    # Print System information
    print("------- Board Information -------")
    for k,v in GPIO.RPI_INFO.items():
        print(f"{k}: {v}")
    print(f"GPIO Version: {GPIO.VERSION}")
    print("------- Arducam Depth Camera -------")
    print("SDK version:", ac.__version__)
    print("------------------------------------")
    
    # create directories if it doesn't exists
    Path(os.getcwd() + '/data/thermal').mkdir(parents=True, exist_ok=True)
    Path(os.getcwd() + '/data/depth').mkdir(parents=True, exist_ok=True)
    Path(os.getcwd() + '/data/images').mkdir(parents=True, exist_ok=True)
    
    # start time
    t1 = time.time()
    
    # Create multiprocessing queue
    queue = mp.Queue()
    
    processes = [
        mp.Process(target=collect_tof_data, args=(mlx, queue,)),
        mp.Process(target=collect_thermal_data, args=(cam, queue,)),
    ]
    
    # start all processes
    for process in processes:
        process.start()
    
    # start post data process
    processData = mp.Process(target=process_data, args=(queue,))
    processData.start()
    
    # join all processes:
    for process in processes:
        process.join()
    
    # add sentinel to the queue to stop processing
    queue.put(None)
    
    # wait for the processor to finish
    processData.join()
    print("All Processing completed.")
    queue.close()
    
    # end time
    t2 = time.time()
    total = t2 - t1
    print(f"Total time: {total:.2f}")
    return 0;

if __name__ == "__main__":
    main()
