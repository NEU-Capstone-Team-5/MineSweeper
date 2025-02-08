import numpy as np
import matplotlib.pyplot as plt
import os

def process_data(file_path: str):
    """Process thermal data and save the processed image."""
    # Load the saved thermal data from the .npz file
    data = np.load(file_path)
    temperature_data = data['temperature']
    print(f"Data loaded from: {file_path}")

    # Setup the figure for plotting
    plt.ion()
    fig, ax = plt.subplots(figsize=(12, 7))
    therm1 = ax.imshow(np.zeros(temperature_data.shape), cmap='plasma', vmin=0, vmax=60)
    cbar = fig.colorbar(therm1)
    cbar.set_label('Temperature [$^{\circ}$C]', fontsize=14)

    # Update the thermal image with the data
    therm1.set_data(np.fliplr(temperature_data))  # Flip left to right
    therm1.set_clim(vmin=np.min(temperature_data), vmax=np.max(temperature_data))  # Set bounds
    cbar.update_normal(therm1)

    # Save the processed thermal image
    folder_path = "thermalImage"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    timestamp = file_path.split('_')[-1].split('.')[0]  # Extract timestamp from the filename
    save_path = os.path.join(folder_path, f"thermal_image_{timestamp}.png")
    fig.savefig(save_path, dpi=300, facecolor='#FCFCFC', bbox_inches='tight')
    print(f"Processed thermal image saved as {save_path}")

    # Close the figure to avoid memory issues
    plt.close(fig)

    # Delete the .npz file after processing
    os.remove(file_path)
    print(f"Deleted {file_path}")


def main():
    # Folder containing the .npz files
    folder_path = 'thermalImage'
    
    # Iterate through all .npz files in the folder
    for npz_file in os.listdir(folder_path):
        if npz_file.endswith('.npz'):
            # Full file path
            file_path = os.path.join(folder_path, npz_file)
            
            # Process the file and delete after saving the image
            process_data(file_path)


if __name__ == "__main__":
    main()

