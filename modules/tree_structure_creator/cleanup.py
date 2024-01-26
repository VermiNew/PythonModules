import os
import shutil
from colorama import init, Fore, Style

init(autoreset=True)

class Cleanup:
    def __init__(self, directory):
        self.directory = directory

    def find_txt_files(self):
        return [file for file in os.listdir(self.directory) if file.endswith('.txt') and file != 'requirements.txt']

    def check_pycache_existence(self):
        return "__pycache__" in os.listdir(self.directory)

    def remove_files(self, files):
        for file in files:
            os.remove(file)
            print(f"{Fore.GREEN}File {Fore.YELLOW}'{file}'{Fore.GREEN} has been removed.")

    def remove_directory(self, directory):
        shutil.rmtree(directory)
        print(f"{Fore.GREEN}Directory {Fore.YELLOW}'{directory}'{Fore.GREEN} has been removed.")

def main():
    directory = os.getcwd()  # Assuming the current working directory
    cleaner = Cleanup(directory)

    txt_files = cleaner.find_txt_files()
    if txt_files:
        print(f"{Fore.LIGHTBLUE_EX}Found txt files: {Fore.RESET}", ", ".join(txt_files))
        confirm = input(f"{Fore.CYAN}Do you want to delete these files? (yes/no): {Style.RESET_ALL}").lower()
        if confirm == 'yes':
            cleaner.remove_files(txt_files)
    else:
        print(f"{Fore.LIGHTMAGENTA_EX}No .txt files found (excluding requirements.txt).")

    if cleaner.check_pycache_existence():
        print(f"{Fore.YELLOW}Found __pycache__ directory.")
        confirm = input(f"{Fore.CYAN}Do you want to delete the __pycache__ directory? (yes/no): {Style.RESET_ALL}").lower()
        if confirm == 'yes':
            cleaner.remove_directory(os.path.join(directory, "__pycache__"))
    else:
        print(f"{Fore.LIGHTMAGENTA_EX}No __pycache__ directory found.")

if __name__ == "__main__":
    main()
