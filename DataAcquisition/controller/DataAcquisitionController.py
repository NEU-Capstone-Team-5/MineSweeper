# import libraries
import multiprocessing as mp
import time
import typing
import logging
from logging.handlers import QueueHandler, QueueListener

class DataAcquisitionController():
    """Creates a controller for Data Acquisition."""
    def __init__(self, num_processes=3, log_level=logging.INFO):
        """ Initializes Data Acquistion Controller."""
        # Create Multiprocessing Pool
        self.pool = mp.Pool(processes=num_processes)
        # create multiprocessing queue for data queues
        self.data_queue = mp.Queue(maxsize=400) # Optional for now (no processing will be done after)
        
        # Store sensor configurations
        self.sensor_configs = {} 
        self.sensor_processes = {}
        
        # Create a multiprocessing event flag
        self.running = mp.Event() 
        self.running.set() # Set the flag to True initially\
        
        # Multiprocessing logging
        self.log_queue = mp.Queue(-1)
        self.logger = self._setup_logger(log_level, self.log_queue)
        
        # Create a"real" handler
        real_handler = logging.FileHandler("temp.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        real_handler.setFormatter(formatter)

        # Create the QueueListener (in the main process)
        self.listener = QueueListener(self.log_queue, real_handler)
        self.listener.start()  # Start the listener
        
    def _setup_logger(self, log_level, log_queue):
        """ Sets up the logger."""
        # initlaize logging object
        logger = logging.getLogger(__name__)
        logger.setLevel(log_level)
        
        # initialize queue handler 
        handler = QueueHandler(log_queue)
        
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
        self.logger.info(f"Sensor config added for '{sensor_name}'.")
    
    def _run_sensor(self, sensor_class, sensor_name, *args, **kwargs):
        """Internal method to run the sensor process.
        
            Args:
                sensor_name (str): sensor name
                sensor_class (BaseSensor): sensor object
                args (Optional): additional positional argument
                kwargs (typing.Dict): additional keyword arguments
        """
        try:
            sensor = sensor_class(sensor_name, self.data_queue, self.running, 
                                  self.logger, *args, **kwargs)
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
            
            # add to running sensor_process
            self.sensor_processes[sensor_name] = config
                
    def stop_all_sensors(self):
        """Stops all running sensors."""
        self.running.clear() # Clear running event flag
        self.pool.close()
        self.pool.join()
        self.logger.info("Process pool stopped.")
        self.listener.stop()
        
    def get_sensor_data(self):
        """Retrieves data from a sensor's queue."""
        try:
            # Check for error message in the queue
            item = self.data_queue.get_nowait()
            if isinstance(item, dict) and item.get("type") == "error":
                self.logger.error(f"Error received from {item['sensor']}: {item['message']}")
                self.stop_all_sensors()
                return None  # Or raise an exception

            return item
        except mp.queues.Empty:
            return None
        
    def get_sensor_queue(self):
        """Returns the data queue buffer."""
        return self.data_queue
    