import open3d as o3d
import numpy as np
import glob
import cv2
import os
from DataProcessor.utils.utils import get_intrinsic, filter_buffer, rgbd_image, z_depth, filter_by_luminance

def create_visualizer(shape=(640,480), pointsize=2.0, bgcolor=(0, 0, 0)):
    # vis = o3d.visualization.Visualizer()
    vis = o3d.visualization.Visualizer()

    vis.create_window("Point Cloud", shape[0], shape[1])

    
    return vis

if __name__ == '__main__':
    
    rgb_paths = glob.glob(pathname='/rgb/rgb*.png', root_dir='~/MineSweeper/data')
    depth_paths = glob.glob(pathname='/depth/tof*.png', root_dir='~/MineSweeper/data')
    
    pcd_list = []
    
    try:
        for i in range(len(depth_paths)):
            rgb_data = np.load(rgb_data[i])
            depth_data = np.load(depth_paths[i])
            
            color = rgb_data['rgb']
            depth = depth_data['depth']
            amplitude = depth_data['confidence']
            
            depth = filter_buffer(depth, amplitude, 0.3)
            
            tof_intrinsic = get_intrinsic()
            
            zdepth = z_depth(depth=depth, intrinsic=tof_intrinsic)
            
            rgbd_img = rgbd_image(color, depth)
            
            pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd_img, tof_intrinsic)
            
            pcd = filter_by_luminance(pcd, confidence=20)
            
            o3d.io.write_point_cloud(f"~/MineSweeper/data/pointcloud/pcd_rgbd_{i}.ply", pcd, write_ascii=False)
            
            pcd_list.append(pcd)
            
        o3d.visualization.draw_geometries(pcd_list)
    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        