import time
import os
import numpy as np
import ArducamDepthCamera as ac
from datetime import datetime
from DataAcquisition.Controller.BaseSensor import BaseSensor  # Assuming BaseSensor is in the same directory
import multiprocessing as mp
import logging

# MAX_DISTANCE value modifiable 2000 or 4000
MAX_DISTANCE = 4000

class DepthSensor(BaseSensor):
    """
    Collects data from the ToF Camera.
    """
    def __init__(self, sensor_name, data_queue, event:mp.Event, logger: logging.Logger, args, kwargs): # type: ignore
        super().__init__(sensor_name, data_queue, event, logger, args, kwargs)
        self.tof = ac.ArducamCamera()

        # check if port is found
        if ("port" in kwargs):
            self.port = kwargs["port"]
            self.logger.info(f"ToF Port: {self.port}")
        else:
            self.port = 8 # Default to CSI Port 1
        
        
    def _setup_camera(self):
        """
        Opens and starts the ToF camera.
        """
        # Attempt connection to CSI Ports
        if (self.port != -1):
            ret = self.tof.open(ac.Connection.CSI, self.port)
            self.logger.info(f"Opened Depth Sensor on port {self.port}.")
        else:
            self.logger.error(f"Couldn't find connection to Depth Sensor.")
        
        if ret != 0:
            self.logger.error(f"Failed to open ToF camera. Error code:{ret}")

        # Attempt to start ToF Camera
        ret = self.tof.start(ac.FrameType.DEPTH)
        if ret != 0:
            self.tof.close()
            self.logger.error(f"Failed to start ToF camera. Error code:{ret.value}")
            
        # Change Range to 4m
        self.tof.setControl(ac.Control.RANGE, 4000)
        self._range = self.tof.getControl(ac.Control.RANGE)
        
        self._info = self.tof.getCameraInfo()
        self.logger.info(f"Camera Resolution: {self._info.width}x{self._info.height}")
        
        
    def acquire_data(self, nFrames):
        """
        Acquires a single depth frame.

        Returns:
            dict: A dictionary containing the sensor data.
        """
        try:
            frame = self.tof.requestFrame(1000)  # set timeout to 1s
            self.logger.info("ToF Frame received")
            if frame is not None and isinstance(frame, ac.DepthData):
                # Get Depth Data
                depth_buf = frame.depth_data                # np.float32
                amplitude_buf = frame.amplitude_data        # np.float32
                confidence_buf = frame.confidence_data      # np.float32
                
                # Get Camera Intrinsic Matrix
                intrinsic = np.eye(3)
                intrinsic[0][0] = self.tof.getControl(ac.Control.INTRINSIC_FX)
                intrinsic[0][2] = self.tof.getControl(ac.Control.INTRINSIC_CX)
                intrinsic[1][1] = self.tof.getControl(ac.Control.INTRINSIC_FY)
                intrinsic[1][2] = self.tof.getControl(ac.Control.INTRINSIC_CY)
                
                # Get timestamp
                now = datetime.now()
                timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
                
                # save data to .npz file
                npz_path = (self.data_dir + f"/depth/tof_{nFrames}.npz")
                np.savez(npz_path, timestamp=timestamp, depth=depth_buf, 
                         amplitude=amplitude_buf, confidence=confidence_buf,
                         intrinsic=intrinsic)
                
                # package data to queue
                data = {
                    "sensor": "depth",
                    "timestamp": timestamp,
                    "path": npz_path
                }
                
                # release the frame
                self.tof.releaseFrame(frame)
                return data
            return None
        except Exception as e:
            self.logger.error(f"Error acquiring ToF data: {e}")
            return None
    
    def run(self):
        """
        Continuously collects ToF data and puts it into the data queue.
        """
        self.logger.info("Running ToF Process")
        self._setup_camera()
        
        try:
            nFrames = 0
            while self.running.is_set() and nFrames < self.num_frames:
                data = self.acquire_data(nFrames)
                self.logger.info("ToF Frame Captured")
                if data:
                    self.data_queue.put(data)
                time.sleep(self.delay)
                nFrames += 1
        except KeyboardInterrupt:
            self.logger.warning("ToF Collection stopped from KeyboardInterrupt")
        except Exception as e:
            self.logger.error("Error with Depth Camera.")
            self.data_queue.put({
                "type": "error",
                "sensor": self.sensor_name,
                "message": str(e)
            })
        finally:
            self.stop()
    
    def stop(self):
        """
        Stops the ToF data collection.
        """
        self.tof.stop()
        self.tof.close()
        self.logger.info("ToF sensor stopped.")