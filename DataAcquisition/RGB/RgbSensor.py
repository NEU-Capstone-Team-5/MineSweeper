import time
import numpy as np
import picamera2 as pi_cam
from libcamera import controls
from datetime import datetime
from DataAcquisition.Controller.BaseSensor import BaseSensor  # Assuming BaseSensor is in the same directory
import logging
import multiprocessing as mp

class RgbSensor(BaseSensor):
    """
    Collects data from the RGB Camera.
    """
    def __init__(self, sensor_name, data_queue, event:mp.Event, logger: logging.Logger, *args, **kwargs):
        super().__init__(sensor_name, data_queue, event, logger, args, kwargs)
        
        # get resolution from constructor
        if ("resolution" in kwargs):
            self.resolution = kwargs["resolution"]
        else :
            self.resolution = (1920, 1080) # default resolution to take
        
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
        
    def acquire_data(self, nFrames):
        """
        Acquires a single RGB frame.

        Returns:
            dict: A dictionary containing the sensor data.
        """
        try:
            image_buf = np.empty((self.resolution[1] * self.resolution[0] * 3,), dtype=np.uint8)
            image_buf = self.cam.capture_array("main")
            self.logger.info(f"Image Frame Captured")
            
            image = image_buf.reshape((self.resolution[1], self.resolution[0], 4))
            
            now = datetime.now()
            timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
            
            # save data to .npz file
            npz_path = (self.data_dir + f"/rgb/rgb_{nFrames}.npz")
            np.savez(npz_path, timestamp=timestamp, rgb=image)
            self.logger.info(f"Saving RGB Data at {npz_path}.")
            
            data = {
                "sensor": "rgb",
                "timestamp": timestamp,
                "path": npz_path
            }
            return data
        except Exception as e:
            self.logger.error(f"Error acquiring RGB data: {e}")
            return None
   
    def run(self):
        """
        Continuously collects RGB data and puts it into the data queue.
        """
        try:
            nFrames = 0
            while self.running.is_set() and nFrames < self.num_frames:
                data = self.acquire_data(nFrames)
                if data:
                    self.data_queue.put(data)
                time.sleep(self.delay)  # Adjust as needed
                nFrames += 1
        except KeyboardInterrupt:
            self.logger.error(f"RGB Collection Stopped from KeyboardInterrupt")
        except Exception as e:
            self.logger.error(f"RGB Found an Error.")
            self.data_queue.put({
                "type": "error",
                "sensor": self.sensor_name,
                "message": str(e)
            })
        finally:
            self.stop()
    
    def stop(self):
        """
        Stops the RGB data collection.
        """
        self.logger.info("RGB sensor stopped.")
        self.cam.close()
        self.cam.stop()
        super().stop()
       