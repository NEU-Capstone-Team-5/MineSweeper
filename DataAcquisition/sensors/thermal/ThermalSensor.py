import time
import os
import numpy as np
import adafruit_mlx90640 as thermal_cam
import busio
import board
from datetime import datetime
from controller import BaseSensor
import multiprocessing as mp
import logging

class ThermalSensor(BaseSensor):
    """
    Collects data from the Thermal Camera.
    """
    def __init__(self, sensor_name, data_queue, event: mp.Event, 
                 logger: logging.Logger, refresh_rate=thermal_cam.RefreshRate.REFRESH_8_HZ):
        super().__init__(sensor_name, data_queue, event, logger)
        self.refresh_rate = refresh_rate
        self.mlx_shape = (24, 32)
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.mlx = thermal_cam.MLX90640(self.i2c)
        self.mlx.refresh_rate = self.refresh_rate
        
    def acquire_data(self):
        """
        Acquires a single thermal frame.

        Returns:
            dict: A dictionary containing the sensor data.
        """
        try:
            frame = np.zeros((24 * 32,))
            self.mlx.getFrame(frame)
            data_array = np.reshape(frame, self.mlx_shape)
            print("Thermal Frame Received")
            
            now = datetime.now()
            timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
            
            # save data to .npz file
            npz_path = (os.getcwd() + f"/data/thermal/mlx90640_{timestamp}.npz")
            np.savez(npz_path, temperature=data_array)
            
            data = {
                "sensor": "thermal",
                "timestamp": timestamp,
                "path": npz_path
            }
            return data
        except Exception as e:
            print(f"Error acquiring thermal data: {e}")
            return None
    
    def run(self, delay=1):
        """
        Continuously collects thermal data and puts it into the data queue.
        """
        try:
            while self.running.is_set():
                data = self.acquire_data()
                if data:
                    self.data_queue.put(data)
                time.sleep(delay)  # Adjust as needed
        except KeyboardInterrupt:
            print(f"Thermal Collection stopped from KeyboardInterrupt")
            self.running.clear() # Stop the sensor
        except Exception as e:
            self.logger.error(f"Error in thermal sensor: {e}")
            self.data_queue.put({
                "type": "error",
                "sensor": self.sensor_name,
                "message": str(e)
            })
            self.running.clear() # Stop the sensor
        finally:
            self.stop()
    
    def stop(self):
        """
        Stops the thermal data collection.
        """
        print("Thermal sensor stopped.")