import os
from tqdm import tqdm

def delete_files_from_folder(folder_path):
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return
    
    # Get the list of files in the folder
    file_list = os.listdir(folder_path)
    
    # If the folder is empty, exit the function
    if not file_list:
        print(f"The folder {folder_path} is empty.")
        return

    # Display the list of files
    print(f"List of files in the folder {folder_path}:")
    for file in file_list:
        print(file)

    # Ask the user for confirmation to delete the files
    confirmation = input(f"\nAre you sure you want to delete {len(file_list)} files from the folder {folder_path}? (yes/no): ")

    if confirmation.lower() != 'yes':
        print("Deletion operation canceled.")
        return

    # Create a progress bar
    with tqdm(total=len(file_list), desc="Deleting files", unit="file") as progress_bar:
        # Delete each file in the folder
        for file in file_list:
            file_path = os.path.join(folder_path, file)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error while deleting the file {file_path}: {e}")
            
            # Update the progress bar
            progress_bar.update(1)

    print(f"All files have been deleted from the folder {folder_path}.")
    
delete_files_from_folder("./mp4")
