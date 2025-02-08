import numpy as np
import ArducamDepthCamera as ac
from datetime import datetime
import os


def save_data(depth_buf, confidence_buf, timestamp):
    # Save the depth and confidence data into a file

    np.savez(f"depthImage/captured_data_{timestamp}.npz", depth=depth_buf, confidence=confidence_buf)


def main():
    print("Arducam Depth Camera Demo.")
    print("  SDK version:", ac.__version__)

    cam = ac.ArducamCamera()
    ret = cam.open(ac.Connection.CSI, 0)
    if ret != 0:
        print("Failed to open camera. Error code:", ret)
        return

    ret = cam.start(ac.FrameType.DEPTH)
    if ret != 0:
        print("Failed to start camera. Error code:", ret)
        cam.close()
        return

    frame_count = 0
    while frame_count < 1:
        frame = cam.requestFrame(2000)
        print("Frame received", frame)
        if frame is not None and isinstance(frame, ac.DepthData):
            frame_count += 1
            depth_buf = frame.depth_data
            confidence_buf = frame.confidence_data

            # Get the timestamp
            now = datetime.now()
            timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"

            # Save data
            save_data(depth_buf, confidence_buf, timestamp)

            cam.releaseFrame(frame)

    cam.stop()
    cam.close()


if __name__ == "__main__":
    main()


