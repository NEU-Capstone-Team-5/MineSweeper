import cv2 as cv
import numpy as np
import glob
import picamera2 as p2
from datetime import datetime
import os

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# chessboard dimensions
chessboard = (8,6) # squares grid dimension

# prepare object points, like (0,0,0) (1,0,0) (2,0,0), ..., (6,5,0)
objp = np.zeros((chessboard[0] * chessboard[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboard[0], 0:chessboard[1]].T.reshape(-1,2)

# arrays to store object points and image points from all the images
objpoints = [] # 3d points in real-world space
imgpoints = [] # 2d points in image plane

images = glob.glob('old_chess.png')

for fname in images:
    print(f"Got image from data folder")
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGRA2GRAY)
    
    # Find the chess board corners 
    ret, corners = cv.findChessboardCorners(gray, chessboard, None)
    
    # if found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        
        corners2 = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)
        
        # Draw and display the corners
        cv.drawChessboardCorners(img, chessboard, corners2, ret)
        
        # Save image to data array
        cv.imwrite('./chess.png', img)

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print(f"Camera matrix:\n {mtx}")
print(f"Distoration Coefficients: {dist}")
print(f"Rotation vector: {rvecs}")
print(f"Translation Vector: {tvecs}")

# get timestamp
now = datetime.now()
timestamp = now.strftime("%H-%M-%S") + f".{now.microsecond // 1000:03d}"
       
# save calibration matrices
matrix_path = os.getcwd() + f"/calibration/rgb/calibration_old_chess.npz"
np.savez(matrix_path, cam_mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

# Refine camera matrix based on scaling parameter
img = cv.imread('old_chess.png')

cam_dim = img.shape[:2]
newCamMtx, roi = cv.getOptimalNewCameraMatrix(mtx, dist, cam_dim, 1, cam_dim)

# undistortion
dst = cv.undistort(img, mtx, dist, None, newCamMtx)

x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv.imwrite('calibratedChess.png', dst)


