import numpy as np
import cv2 as cv
import open3d as o3d
import os

def calculate_fov(shape, fov):
    """Calculates the fov for the x and y axis based on the shape.

    Args:
        shape (np.array): _description_
        fov (int) : 

    Returns:
        np.array: horizontal fov and vertical fov
    """
    aspect_ratio = shape[0] / shape[1]
    fov_rad = np.deg2rad(fov)

    hfov_rad = 2 * np.arctan(np.tan(fov_rad / 2) / np.sqrt(1 + (1 / aspect_ratio**2)))
    vfov_rad = 2 * np.arctan(np.tan(fov_rad / 2) / np.sqrt(1 + aspect_ratio**2))

    hfov = np.rad2deg(hfov_rad)
    vfov = np.rad2deg(vfov_rad)
    return [hfov, vfov]

def get_intrinsic(shape=(240, 180), fov=70):
    fovs = calculate_fov(shape, fov)
    width, height = shape
    
    fx = width / (2 * np.tan(0.5 * np.pi * fovs[0] / 180))
    fy = height / (2 * np.tan(0.5 * np.pi * fovs[1] / 180))
    cx = width / 2
    cy = height / 2
    
    return o3d.camera.PinholeCameraIntrinsic(width, height, fx, fy, cx, cy)

def z_depth(depth, intrinsic):
    height, width = depth.shape
    
    fx = intrinsic.intrinsic_matrix[0,0]
    fy = intrinsic.intrinsic_matrix[1,1]
    cx = intrinsic.intrinsic_matrix[0,2]
    cy = intrinsic.intrinsic_matrix[1,2]
    
    x, y = np.meshgrid(np.arrange(width), np.arrange(height))
    x = (x - cx) / fx
    y = (y - cy) / fy
    
    return (depth / np.sqrt(x**2 + y**2 + 1)).astype(np.float32)

def rgbd_image(color, depth):
    color = cv.cvtColor(color, cv.COLOR_BGR2RGB)
    
    depth_img = o3d.geometry.Image(depth)
    color_img = o3d.geometry.Image(color)
    
    rgbd_img = o3d.geometry.RGBDImage.create_from_color_and_depth(
        color_img, depth_img, depth_scale=1.0, depth_trunc=4000.0, convert_rgb_to_intensity=False
    )
    
    return rgbd_img

def filter_buffer(depth, amplitude, threshold):
    depth = np.nan_to_num(depth)
    depth[amplitude < threshold] = 0
    return depth

def filter_by_luminance(pcd, confidence=20):
    green_channel = np.asarray(pcd.colors)[:, 1]
    mask = green_channel >= (confidence / 255.0)
    pcd = pcd.select_by_index(np.where(mask)[0])
    return pcd




    
    