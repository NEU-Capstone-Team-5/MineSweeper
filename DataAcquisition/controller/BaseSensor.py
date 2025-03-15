""" """
# import libraries
import time
import multiprocessing as mp
import logging
class BaseSensor:
    def __init__(self, sensor_name, data_queue, event: mp.Event, logger: logging.Logger):
        self.sensor_name = sensor_name
        self.data_queue = data_queue
        self.running = event
        self.logger = logger
        
    def run(self):
        self.logger.info(f"{self.sensor_name} started.")
        raise NotImplementedError

    def acquire_data(self, timeout=1000):
        raise NotImplementedError
    
    def stop(self):
        self.logger.info(f"{self.sensor_name} stopped.")