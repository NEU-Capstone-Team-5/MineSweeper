import board
import busio
import numpy as np
import adafruit_mlx90640
from datetime import datetime
import os

def main():
  # Setup I2C
  i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)
  mlx = adafruit_mlx90640.MLX90640(i2c)
  mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ
  mlx_shape = (24, 32)

  # Setup frame for storing temperatures
  frame = np.zeros((24 * 32,))

  # Capture thermal data
  elapsed_time = 0
  while elapsed_time < 1:
    try:
        mlx.getFrame(frame)  # Read MLX temperatures into frame var
        data_array = np.reshape(frame, mlx_shape)  # Reshape to 24x32
        now = datetime.now()
        timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
        # Save data to .npz file
        npz_path = os.path.join("thermalImage", f"thermal_data_{timestamp}.npz")
        np.savez(npz_path, temperature=data_array)
        print(f"Thermal data saved as {npz_path}")

        elapsed_time = 1
    except ValueError:
        continue  # If error, just read again

if __name__ == "__main__":
  main()
