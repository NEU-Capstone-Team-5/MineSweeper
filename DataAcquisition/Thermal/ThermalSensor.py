import time
import os
import numpy as np
import adafruit_mlx90640 as thermal_cam
import busio
import board
from datetime import datetime
from DataAcquisition.Controller.BaseSensor import BaseSensor
import multiprocessing as mp
import logging

class ThermalSensor(BaseSensor):
    """
    Collects data from the Thermal Camera.
    """
    def __init__(self, sensor_name, data_queue, event: mp.Event, logger: logging.Logger, *args, **kwargs):
        super().__init__(sensor_name, data_queue, event, logger)
        self.mlx_shape = (24, 32)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mlx = thermal_cam.MLX90640(self.i2c)
        if ("refresh_rate" in kwargs):
            self.mlx.refresh_rate = kwargs["refresh_rate"]
        else: 
            self.mlx.refresh_rate = thermal_cam.RefreshRate.REFRESH_8_HZ
            
        
    def acquire_data(self, nFrames):
        """
        Acquires a single thermal frame.

        Returns:
            dict: A dictionary containing the sensor data.
        """
        try:
            frame = np.zeros((24 * 32,))
            self.mlx.getFrame(frame)
            data_array = np.reshape(frame, self.mlx_shape)
            self.logger.info("Thermal Frame Received")
            
            now = datetime.now()
            timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
            
            # save data to .npz file
            npz_path = (self.data_dir + f"/thermal/mlx90640_{nFrames}.npz")
            np.savez(npz_path, timestamp=timestamp, temperature=data_array)
            
            data = {
                "sensor": "thermal",
                "timestamp": timestamp,
                "path": npz_path
            }
            return data
        except Exception as e:
            self.logger.error(f"Error acquiring thermal data: {e}")
            return None
    
    def run(self):
        """
        Continuously collects thermal data and puts it into the data queue.
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
            self.logger.error(f"Thermal Collection stopped from KeyboardInterrupt")
        except Exception as e:
            self.logger.error(f"Error in thermal sensor: {e}")
            self.data_queue.put({
                "type": "error",
                "sensor": self.sensor_name,
                "message": str(e)
            })
        finally:
            self.stop()
    
    def stop(self):
        """
        Stops the thermal data collection.
        """
        self.logger.info("Thermal sensor stopped.")