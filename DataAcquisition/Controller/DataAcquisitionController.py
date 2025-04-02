# import libraries
import multiprocessing as mp
import time
import typing
import logging
from logging.handlers import QueueHandler, QueueListener

class DataAcquisitionController():
    """Creates a controller for Data Acquisition."""
    def __init__(self, log_level=logging.INFO, data_dir='/home/team5/MineSweeper'):
        """ Initializes Data Acquistion Controller."""
        # get the location of the data directory
        self.data_dir = data_dir
        
        # create multiprocessing queue for data queues
        self.data_queue = mp.Queue(maxsize=400) # Optional for now (no processing will be done after)
        
        # Store sensor configurations
        self.sensor_configs = {} 
        self.sensor_processes = {}
        
        # Create a multiprocessing event flag
        self.running = mp.Event() 
        self.running.set() # Set the flag to True initially
        
        # Multiprocessing logging
        self.log_queue = mp.Queue()
        self.logger = self._setup_logger(log_level, self.log_queue)
        
        # Create a "real" handler
        real_handler = logging.FileHandler("temp.log")
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # real_handler.setFormatter(formatter)

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
        
        kwargs["data_dir"] = self.data_dir
        
        self.sensor_configs[sensor_name] = {
            "class": sensor_class,
            "args": args,
            "kwargs": kwargs,
        }
        
        self.logger.info(f"Sensor config added for '{sensor_name}'.")
    
    def _run_sensor(self, sensor_class, sensor_name, args, kwargs):
        """Internal method to run the sensor process.
        
            Args:
                sensor_name (str): sensor name
                sensor_class (BaseSensor): sensor object
                args (Optional): additional positional argument
                kwargs (typing.Dict): additional keyword arguments
        """
        try:
            self.logger.info(f"Attempting to start {sensor_name}'s process")
            sensor = sensor_class(sensor_name, self.data_queue, self.running, 
                                  self.logger, args, kwargs)
            self.logger.info(f"Created {sensor_name} class object.")
            sensor.run() #The sensor will run forever, until stopped.
        except Exception as e:
            self.logger.error(f"Error in sensor '{sensor_name}' process: {e}")
            raise
        
    def start_all_sensors(self):
        """Starts all configured sensors."""
        # traverse through sensor configurations and create the Processes
        for sensor_name, config in self.sensor_configs.items():
            # Check if the sensor already exists
            if sensor_name in self.sensor_processes:
                self.logger.warning(f"Sensor '{sensor_name}' already running. Skipping.")
                continue
            
            # create Process obj
            curr_process = mp.Process(target=self._run_sensor,
                                args=(config["class"], sensor_name, config["args"], config["kwargs"]))
            
            config["process"] = curr_process
            config["process_id"] = curr_process.pid
            
            # add to running sensor_process
            self.logger.info(f"Created {sensor_name} process.")
            self.sensor_processes[sensor_name] = config
            
        # start the current process
        for curr_process in self.sensor_processes:
           
            self.logger.info(f"Started {sensor_name} process.")
            self.sensor_processes[curr_process]["process"].start()
                        
    def join_all_sensors(self):
        """Attempt to join all sensor processes"""
        for sensor_name, p_info in self.sensor_processes.items():
            self.logger.info(f"Attempting to join {sensor_name} process.")
            p_info["process"].join()
        
        time.sleep(1)
        # stop all sensors
        self.stop_all_sensors()
            
    def stop_all_sensors(self):
        """Stops all running sensors."""
        self.running.clear() # Clear running event flag
        self.logger.info("Process pool stopped.")
        time.sleep(0.1)
        self.listener.stop()
        time.sleep(0.1)
        for handler in self.listener.handlers:
            handler.flush()
            handler.close()
        logging.shutdown()
        
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
    