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
    controller.add_sensor_config("rgb", RgbSensor, resolution=(1920,1080), num_frames = 10)
    
    # Determine Depth Camera Port
    ret = -1
    tof = ac.ArducamCamera()
    port = -1
    for i in range(16):
        try:
            ret = tof.open(ac.Connection.CSI, i)
            if (ret == 0):
                port = i
        except Exception as e:
            continue
    if port == -1:
        print(f"Error: Cannot find DepthSensor.")
    else:
        tof.close()
        # add depth camera to controller if found
        # controller.add_sensor_config("tof", DepthSensor, num_frames = 10, port=port)
    del tof
    
    # controller.add_sensor_config("thermal", ThermalSensor, refresh_rate=thermal_cam.RefreshRate.REFRESH_8_HZ, num_frames = 10)
    
    # run the sensors
    print(f"----- Starting Sensors Processes -----\n")
    controller.start_all_sensors()
    
    time.sleep(1)
    
    controller.join_all_sensors()
    
    
    