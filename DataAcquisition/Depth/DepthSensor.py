import time
import os
import numpy as np
import ArducamDepthCamera as ac
from datetime import datetime
from DataAcquisition.Controller.BaseSensor import BaseSensor  # Assuming BaseSensor is in the same directory
import multiprocessing as mp
import logging
import subprocess
class DepthSensor(BaseSensor):
    """
    Collects data from the ToF Camera.
    """
    def __init__(self, sensor_name, data_queue, event:mp.Event, logger: logging.Logger, *args, **kwargs):
        super().__init__(sensor_name, data_queue, event, logger, args, kwargs)
        self.tof = ac.ArducamCamera()

        # check if port is found
        if ("port" in kwargs):
            self.port = kwargs["port"]
        else:
            self.port = 8
            
    def _setup_camera(self):
        """
        Opens and starts the ToF camera.
        """
        if (self.port != -1):
            ret = self.tof.open(ac.Connection.CSI, self.port)
            self.logger.info(f"Opened Depth Sensor on port {self.port}.")
        else:
            self.logger.error(f"Couldn't find connection to Depth Sensor.")
            
        if ret != 0:
            self.logger.error(f"Failed to open ToF camera. Error code:{ret}")

        ret = self.tof.start(ac.FrameType.DEPTH)
        if ret != 0:
            self.tof.close()
            self.logger.error(f"Failed to start ToF camera. Error code:{ret}")
            
    def acquire_data(self):
        """
        Acquires a single depth frame.

        Returns:
            dict: A dictionary containing the sensor data.
        """
        try:
            frame = self.tof.requestFrame(2000)  # set timeout to 2s
            self.logger.info("ToF Frame received")
            if frame is not None and isinstance(frame, ac.DepthData):
                depth_buf = frame.depth_data
                confidence_buf = frame.confidence_data
                
                now = datetime.now()
                timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
                
                # save data to .npz file
                npz_path = (self.data_dir + f"/depth/tof_{timestamp}.npz")
                np.savez(npz_path, depth=depth_buf, confidence=confidence_buf)
                
                data = {
                    "sensor": "depth",
                    "timestamp": timestamp,
                    "path": npz_path
                }
                
                self.tof.releaseFrame(frame)
                return data
            return None
        except Exception as e:
            self.logger.error(f"Error acquiring ToF data: {e}")
            return None
    
    def run(self, delay=1):
        """
        Continuously collects ToF data and puts it into the data queue.
        """
        self.logger.info("Running ToF Process")
        self._setup_camera()
        
        try:
            nFrames = 0
            while self.running.is_set() and nFrames < self.num_frames:
                data = self.acquire_data()
                self.logger.info("ToF Frame Captured")
                if data:
                    self.data_queue.put(data)
                time.sleep(delay)
                nFrames += 1
        except KeyboardInterrupt:
            self.logger.warning("ToF Collection stopped from KeyboardInterrupt")
        finally:
            self.stop()
    
    def stop(self):
        """
        Stops the ToF data collection.
        """
        self.tof.stop()
        self.tof.close()
        self.logger.info("ToF sensor stopped.")