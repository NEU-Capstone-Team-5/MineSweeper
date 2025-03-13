""" 
"""
# import libraries
import time

class BaseSensor:
    def __init__(self, sensor_name, data_queue):
        self.sensor_name = sensor_name
        self.data_queue = data_queue
        self.running = False
        
    def run(self):
        raise NotImplementedError

    def acquire_data(self, timeout=1000):
        raise NotImplementedError
    
    def stop(self):
        raise NotImplementedError