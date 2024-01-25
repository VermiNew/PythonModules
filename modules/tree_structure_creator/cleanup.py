import os
import shutil

class Cleanup:
    def __init__(self, directory):
        self.directory = directory

    def find_txt_files(self):
        return [file for file in os.listdir(self.directory) if file.endswith('.txt')]

    def check_pycache_existence(self):
        return "__pycache__" in os.listdir(self.directory)

    def remove_files(self, files):
        for file in files:
            os.remove(file)
            print(f"File '{file}' has been removed.")

    def remove_directory(self, directory):
        shutil.rmtree(directory)
        print(f"Directory '{directory}' has been removed.")

def main():
    directory = os.getcwd()  # Assuming the current working directory
    cleaner = Cleanup(directory)

    txt_files = cleaner.find_txt_files()
    if txt_files:
        print("Found txt files:", ", ".join(txt_files))
        confirm = input("Do you want to delete these files? (yes/no): ").lower()
        if confirm == 'yes':
            cleaner.remove_files(txt_files)

    if cleaner.check_pycache_existence():
        print("Found __pycache__ directory.")
        confirm = input("Do you want to delete the __pycache__ directory? (yes/no): ").lower()
        if confirm == 'yes':
            cleaner.remove_directory(os.path.join(directory, "__pycache__"))

if __name__ == "__main__":
    main()
