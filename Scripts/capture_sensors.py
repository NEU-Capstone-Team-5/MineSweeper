import threading
import subprocess
import time
import os
def run_script(script_name, base_dir):
    """Function to run a script using subprocess."""
    script_name = os.path.join(base_dir, script_name)  # Get full path to the script
    print(f"Running {script_name}...")
    subprocess.run(["python3", script_name])  # Replace with the actual path to your script
    print(f"Finished running {script_name}")

def thread_function(script_name, base_dir):
    """Wrapper to run a script on a separate thread."""
    run_script(script_name, base_dir)


def delete_files_in_directory(directory):
    """Delete all files in the specified directory."""
    # Check if there are files to remove
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    
    if not files:
        print(f"No files to delete in {directory}.")
        return

    # Run the shell command to delete all files (with force)
    subprocess.run(f'rm -f {directory}/*', check=True, shell=True)
    print(f"All files deleted in {directory}")



def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Define subdirectories
    subdirs = ['depthImage', 'thermalImage'] 
    # Delete files in each subdirectory
    for subdir in subdirs:
        subdir_path = os.path.join(base_dir, subdir)
        if os.path.isdir(subdir_path):
            delete_files_in_directory(subdir_path)
        else:
            print(f"{subdir} does not exist.")

    # List of the first set of scripts to run concurrently
    first_scripts = ["capture_depth_data.py", "capture_thermal_data.py"]
    
    # Create threads for the first set of scripts
    threads = []
    for script in first_scripts:
        thread = threading.Thread(target=thread_function, args=(script, base_dir))
        threads.append(thread)
        thread.start()
    
    # Wait for the first set of scripts to finish
    for thread in threads:
        thread.join()
    
    print("First set of scripts finished.")
    
    # List of the second set of scripts to run concurrently
    second_scripts = ["process_depth_data.py", "process_thermal_data.py"]
    
    # Create threads for the second set of scripts
    threads = []
    for script in second_scripts:
        thread = threading.Thread(target=thread_function, args=(script, base_dir))
        threads.append(thread)
        thread.start()
    
    # Wait for the second set of scripts to finish
    for thread in threads:
        thread.join()
    
    print("Second set of scripts finished.")

if __name__ == "__main__":
    main()

