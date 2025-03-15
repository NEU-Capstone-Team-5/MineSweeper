import time
import os
import numpy as np
import picamera2 as pi_cam
from libcamera import controls
from datetime import datetime
from controller import BaseSensor  # Assuming BaseSensor is in the same directory
import logging


class RgbSensor(BaseSensor):
    """
    Collects data from the RGB Camera.
    """
    def __init__(self, sensor_name, data_queue, event:mp.Event, logger: logging.Logger, resolution=(1920, 1080), *args, **kwargs):
        super().__init__(sensor_name, data_queue, event, logger)
        self.resolution = resolution
        self.cam = pi_cam.Picamera2()
        self._setup_camera()
        
    def _setup_camera(self):
        """
        Configures and starts the RGB camera.
        """
        config = self.cam.create_still_configuration(main={"size": self.resolution, "format": "XRGB8888"})
        self.cam.configure(config)
        self.cam.start()
        self.cam.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        
    def acquire_data(self):
        """
        Acquires a single RGB frame.

        Returns:
            dict: A dictionary containing the sensor data.
        """
        try:
            image_buf = self.cam.capture_array("main")
            print(f"Image Frame Captured")
            
            image = image_buf.reshape((self.resolution[1], self.resolution[0], 4))
            
            now = datetime.now()
            timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
            
            # save data to .npz file
            npz_path = ( + f"/data/rgb/rgb_{timestamp}.npz")
            np.savez(npz_path, rgb=image)
            
            data = {
                "sensor": "rgb",
                "timestamp": timestamp,
                "path": npz_path
            }
            return data
        except Exception as e:
            print(f"Error acquiring RGB data: {e}")
            return None
    
    def run(self):
        """
        Continuously collects RGB data and puts it into the data queue.
        """
        self.running = True
        try:
            while self.running:
                data = self.acquire_data()
                if data:
                    self.data_queue.put(data)
                time.sleep(1)  # Adjust as needed
        except KeyboardInterrupt:
            print(f"RGB Collection Stopped from KeyboardInterrupt")
        finally:
            self.stop()
    
    def stop(self):
        """
        Stops the RGB data collection.
        """
        self.running = False
        self.cam.close()
        print("RGB sensor stopped.")