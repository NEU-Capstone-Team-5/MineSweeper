import os
import time
import multiprocessing as mp
from pathlib import Path
import logging

# Import Data Acquisition classes
from DataAcquisition.controller import BaseSensor, DataAcquisitionController
from DataAcquisition.sensors.thermal import ThermalSensor
from DataAcquisition.sensors.depth import DepthSensor
from DataAcquisition.sensors.rgb import RgbSensor
from DataAcquisition.utils.script_path import get_script_dir

# Import Sensor Libraries

def main():
    # --- Initialization ---
    script_dir = get_script_dir()
    data_dir = os.path.join(script_dir, 'data')

    # create directories if it doesn't exists
    Path(os.path.join(data_dir, 'thermal')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(data_dir, 'depth')).mkdir(parents=True, exist_ok=True)
    Path(os.path.join(data_dir, 'rgb')).mkdir(parents=True, exist_ok=True)
    
    # Create Data Acquisition Controller Object
    controller = DataAcquisitionController(num_processes=3, log_level=logging.INFO)
    
    # Add sensor configurations to the controller
    controller.add_sensor_config("thermal", ThermalSensor)
    controller.add_sensor_config("tof", DepthSensor)
    controller.add_sensor_config("rgb", RgbSensor, resolution=(1920,1080))