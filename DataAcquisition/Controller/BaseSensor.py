""" """
# import libraries
import time
import multiprocessing as mp
import logging

class BaseSensor:
    def __init__(self, sensor_name, data_queue, event: mp.Event, logger: logging.Logger, args, kwargs):
        self.sensor_name = sensor_name
        self.data_queue = data_queue
        self.running = event
        self.logger = logger
        
        # set default num frames to 10
        if ("num_frames" in kwargs):
            self.num_frames = kwargs["num_frames"]
        else:
            self.num_frames = 10
        self.logger.info(f"Collecting {self.num_frames} for {self.sensor_name}")
        
        # set default data directory
        if ("data_dir" in kwargs):
            self.data_dir = kwargs["data_dir"]
        else:
            self.data_dir = "/home/team5/MineSweeper/data"
        
        # get delay from constructor
        if ("delay" in kwargs):
            self.delay = kwargs["delay"]
        else:
            self.delay = 1.0

        self.logger.info(f"Created BaseSensor class for {sensor_name}")
        
    def run(self):
        self.logger.info(f"{self.sensor_name} started.")
        raise NotImplementedError

    def acquire_data(self, timeout=1000):
        raise NotImplementedError
    
    def stop(self):
        self.logger.info(f"{self.sensor_name} stopped.")
        self.running.clear()