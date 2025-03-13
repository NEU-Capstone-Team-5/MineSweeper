"""
File: DataAcquisitionController.py
Author: Alston Liu
Date: March 11th 2025
Description:

"""
# import libraries
import multiprocessing
import time

class DataAcquisitionController:
    def __init__(self):
        self.processes = []
        self.data_queues = {}
        
    def create_sensor_process():
        raise NotImplementedError
    
    def _run_sensor(self):
        raise NotImplementedError
    
    def start_all_processes(self):
        raise NotImplementedError
    
    def stop_all_processes(self):
        raise NotImplementedError
    
    def get_sensor_data(self, sensor_name):
        raise NotImplementedError
    
    