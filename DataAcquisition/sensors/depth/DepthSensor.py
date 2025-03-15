import time
import os
import numpy as np
import ArducamDepthCamera as ac
from datetime import datetime
from controller import BaseSensor  # Assuming BaseSensor is in the same directory
import multiprocessing as mp
import logging

class TofSensor(BaseSensor):
    """
    Collects data from the ToF Camera.
    """
    def __init__(self, sensor_name, data_queue, event:mp.Event, logger: logging.Logger, *args, **kwargs):
        super().__init__(sensor_name, data_queue, event, logger)
        self.tof = ac.ArducamCamera()
        self.args = args
        self.kwargs = kwargs

    def _setup_camera(self):
        """
        Opens and starts the ToF camera.
        """
        ret = -1
        for i in range(15):
            try:
                ret = self.tof.open(ac.Connection.CSI, i)
                if ret == 0:
                    break
            except:
                continue
        
        if ret != 0:
            raise Exception("Failed to open ToF camera. Error code:", ret)

        ret = self.tof.start(ac.FrameType.DEPTH)
        if ret != 0:
            self.tof.close()
            raise Exception("Failed to start ToF camera. Error code:", ret)
            
    def acquire_data(self):
        """
        Acquires a single depth frame.

        Returns:
            dict: A dictionary containing the sensor data.
        """
        try:
            frame = self.tof.requestFrame(2000)  # set timeout to 2s
            print("ToF Frame received")
            if frame is not None and isinstance(frame, ac.DepthData):
                depth_buf = frame.depth_data
                confidence_buf = frame.confidence_data
                
                now = datetime.now()
                timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
                
                # save data to .npz file
                npz_path = (os.getcwd() + f"/data/depth/tof_{timestamp}.npz")
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
            print(f"Error acquiring ToF data: {e}")
            return None
    
    def run(self, delay=1):
        """
        Continuously collects ToF data and puts it into the data queue.
        """
        self._setup_camera()
        try:
            while self.running:
                data = self.acquire_data()
                if data:
                    self.data_queue.put(data)
                time.sleep(delay) 
        except KeyboardInterrupt:
            self.logger.warning("ToF Collection stopped from KeyboardInterrupt")
        finally:
            self.stop()
    
    def stop(self):
        """
        Stops the ToF data collection.
        """
        self.running = False
        self.tof.stop()
        self.tof.close()
        print("ToF sensor stopped.")