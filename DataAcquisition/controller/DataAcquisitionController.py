"""
File: DataAcquisitionController.py
Author: Alston Liu
Date: March 11th 2025
Description:

"""
# import libraries
import multiprocessing as mp
import time
import typing
import logging

class DataAcquisitionController():
    def __init__(self, num_processes=3, log_level=logging.INFO):
        """ Initializes Data Acquistion Controller."""
        self.pool = mp.Pool(processes=num_processes) # Create Multiprocessing pool
        self.sensor_configs = {} # Store sensor configurations
        self.logger = self._setup_logger(log_level)  # Create logging stream
        self.data_queue = mp.Queue(maxsize=400) # create multiprocessing 
        
    def _setup_logger(self, log_level):
        """ Sets up the logger."""
        # initlaize logging object
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        
        # initialize stream handler 
        handler = logging.StreamHandler()
        
        # initalize formatter for logging
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
        
    def add_sensor_config(self, sensor_name, sensor_class, *args, **kwargs):
        """Add a sensor configuration.

        Args:
            sensor_name (str): sensor name
            sensor_class (BaseSensor): sensor object
            args (typing.List): 
        Returns:
            (int): Error Code
        """
        if sensor_name in self.sensor_configs:
            self.logger.warning(f"Sensor config for '{sensor_name}' already exists. Overwriting...")
            
        self.sensor_configs[sensor_name] = {
            "class": sensor_class,
            "args": args,
            "kwargs": kwargs,
        }
        self.loggeer.info(f"Sensor config added for '{sensor_name}'.")
    
    def _run_sensor(self, sensor_class, sensor_name, args, kwargs):
        """Internal method to run the sensor process.
        
            Args:
                sensor_name (str): sensor name
                sensor_class (BaseSensor): sensor object
                args (Optional): additional positional argument
                kwargs (typing.Dict): additional keyword arguments
        """
        try:
            sensor = sensor_class(sensor_name, self.data_queue, *args, **kwargs)
            sensor.run() #The sensor will run forever, until stopped.
        except Exception as e:
            self.logger.error(f"Error in sensor '{sensor_name}' process: {e}")
            raise
        
    def start_all_sensors(self):
        """Starts all configured sensors."""
        results = []
        # traverse through sensor configurations
        for sensor_name, config in self.sensor_configs.items():
            # Check if the sensor already exists
            if sensor_name in self.sensor_processes:
                self.logger.warning(f"Sensor '{sensor_name}' already running. Skipping.")
                continue
            
            # initialize a multiprocessing queue for each sensor
            results.append(self.pool.apply_async(self._run_sensor,
                                                 args=(config["class"], sensor_name, config["args"], config["kwargs"])))
        
        # Wait for all processes to start.
        for result in results:
            try:
                self.logger.info(result.get())
            except Exception as e:
                self.logger.error(f"Error in sensor '{sensor_name}' process: {e}")
                
    def stop_all_sensors(self):
        """Stops all running sensors."""
        self.pool.close()
        self.pool.join()
        self.logger.info("Process pool stopped.")
    
    def get_sensor_data(self):
        """Retrieves data from a sensor's queue."""
        raise NotImplementedError
        
    def get_sensor_queue(self):
        """Returns the data queue buffer."""
        return self.data_queue
    