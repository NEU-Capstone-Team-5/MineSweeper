import os
import time
import multiprocessing as mp
from pathlib import Path
import logging

# Import Data Acquisition classes
from DataAcquisition.Controller.DataAcquisitionController import DataAcquisitionController
from DataAcquisition.Thermal.ThermalSensor import ThermalSensor
from DataAcquisition.Depth.DepthSensor import DepthSensor
from DataAcquisition.RGB.RgbSensor import RgbSensor
from DataAcquisition.utils.script_path import get_script_dir
import ArducamDepthCamera as ac
import adafruit_mlx90640 as thermal_cam

if __name__ == "__main__":
    # --- Initialization ---
    script_dir = get_script_dir(__file__)
    data_dir = os.path.join(script_dir, 'data')
    print(f"----- Starting Main Script -----\n")
    
    # create directories if it doesn't exists
    print(f"----- Creating Data Directory -----\n")
    Path(os.path.join(data_dir, 'thermal')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(data_dir, 'depth')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(data_dir, 'rgb')).mkdir(parents=True, exist_ok=True)
    
    # Create Data Acquisition Controller Object
    print(f"----- Initializing Controller Object ------\n")
    controller = DataAcquisitionController(log_level=logging.INFO, data_dir= data_dir)

    # Add sensor configurations to the controller
    controller.add_sensor_config("rgb", RgbSensor, resolution=(640,480), num_frames = 100, delay=0.25)

    # Determine Depth Camera Port
    ret = -1
    tof = ac.ArducamCamera()
    
    # Cycle through the port
    port = -1
    for i in range(16):
        try:
            ret = tof.open(ac.Connection.CSI, i)
            if (ret == 0):
                port = i
                tof.close()
                break
        except Exception as e:
            continue
    
    # Check if the port is found
    if port == -1:
        print(f"Error: Cannot find DepthSensor.")
    else:
        # add depth camera to controller if found
        controller.add_sensor_config("tof", DepthSensor, num_frames = 100, port=port, delay=0.25)
    del tof
    time.sleep(1)
    
    controller.add_sensor_config("thermal", ThermalSensor, refresh_rate=thermal_cam.RefreshRate.REFRESH_8_HZ, num_frames = 100, delay=0.25)
    
    # run the sensors
    print(f"----- Starting Sensors Processes -----\n")
    controller.start_all_sensors()
    
    time.sleep(1)
    
    controller.join_all_sensors()
    
    
    
