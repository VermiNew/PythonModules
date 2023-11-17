import curses
import hashlib
import os
import shutil
import tempfile
import time
import logging
from progressbar_curses.progressbar import ProgressBar

# Configure the logging module
logging.basicConfig(filename='copy_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def copy_file_with_progress(stdscr, source_path, destination_path, filename, progress_bar):
    try:
        total_size = os.path.getsize(source_path)
        copied_size = 0

        progress_bar.set_total_steps(total_size)
        progress_bar.set_message(f"Copying file {filename}...")

        with open(source_path, 'rb') as source_file, open(destination_path, 'wb') as dest_file:
            while True:
                chunk = source_file.read(int(total_size / 16))
                if not chunk:
                    break

                dest_file.write(chunk)
                copied_size += len(chunk)

                progress = copied_size / total_size
                status_message = f"Copying - {copied_size}/{total_size} bytes"
                progress_bar.set_status_message(status_message)
                progress_bar.update_progress_bar(stdscr, progress)
                time.sleep(0.05)

        return True, None
    except Exception as e:
        logging.error(f"Error copying file: {str(e)}")
        return False, str(e)


def copy_folder_with_progress(stdscr, source_folder, destination_folder, progress_bar):
    try:
        # Use the current working directory as the prefix for the temporary folder
        temp_folder = tempfile.mkdtemp(prefix=os.path.join(os.getcwd(), 'temp_'))
        progress_bar.set_message(f"Creating temporary folder: {temp_folder}")

        for foldername, subfolders, filenames in os.walk(source_folder):
            for filename in filenames:
                source_path = os.path.join(foldername, filename)
                relative_path = os.path.relpath(source_path, source_folder)
                destination_path = os.path.join(destination_folder, relative_path)

                logging.info(
                    f"Parameters: temp_folder:{temp_folder} source_folder:{source_folder}"
                    f"destination_folder:{destination_folder}")
                logging.info(f"Source path: {source_path}")
                logging.info(f"Relative path: {relative_path}")
                logging.info(f"Destination path: {destination_path}")

                # Create the destination folder if it doesn't exist
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)

                # Copy the file
                result, error_message = copy_file_with_progress(stdscr, source_path, destination_path, relative_path, progress_bar)
                if not result:
                    logging.error(error_message)
                    raise RuntimeError(error_message)

                # Check the integrity of the data transfer
                if calculate_file_hash(source_path) != calculate_file_hash(destination_path):
                    logging.error(f"Error: Data transfer error - hashes do not match for {filename}")
                    raise RuntimeError(f"Error: Data transfer error - hashes do not match for {filename}")

                # Display file information
                progress_bar.set_message(f"File: {filename} copied and hashed")

        # Remove the temporary folder
        logging.info(f"Deleted temporary folder, {temp_folder}")
        os.rmdir(temp_folder)

        return True, None
    except Exception as e:
        logging.error(f"Error copying folder: {str(e)}")
        return False, str(e)


def calculate_file_hash(file_path, algorithm='md5'):
    hash_function = hashlib.new(algorithm)

    with open(file_path, 'rb') as file:
        while chunk := file.read(4096):
            hash_function.update(chunk)

    return hash_function.hexdigest()


def main(stdscr):
    curses.curs_set(0)  # Wyłącz kursor
    stdscr.clear()

    progress_bar = ProgressBar()

    source_folder_path = "../../Rule34Script/data/kiri"
    destination_folder_path = "./safe_copy_test_destination"

    try:
        # Kopiowanie folderu
        result, error_message = copy_folder_with_progress(stdscr, source_folder_path, destination_folder_path,
                                                          progress_bar)

        if result:
            status_message = "Folder copied successfully!"
        else:
            status_message = f"Error: {error_message}"

        progress_bar.set_message(status_message)
        progress_bar.update_progress_bar(stdscr, 1.0)

    except Exception as e:
        status_message = f"Error: {str(e)}"
        progress_bar.set_message(status_message)
        logging.error(f"Unexpected error: {str(e)}")

    time.sleep(1.5)


curses.wrapper(main)
