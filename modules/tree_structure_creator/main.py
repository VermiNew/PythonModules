import os
import tqdm
import argparse
from colorama import Fore, Style, init, deinit
import ctypes
import re

class TreeStructureCreator:
    def __init__(self, args):
        self.args = args

    @staticmethod
    def is_valid_file_name(file_name):
        return re.match(r'^[\w,\s-]+\.[A-Za-z]{3}$', file_name) is not None

    def count_items(self, path):
        total = 0
        errors = 0

        def log_error(e):
            nonlocal errors
            errors += 1
            self.error_file.write(f"Error accessing {e.filename}: {e.strerror}\n")

        for root, dirs, files in os.walk(path, onerror=log_error):
            total += len(dirs) + len(files)
            if not self.args.silent:
                print(f"{Fore.CYAN}Scanned: {Fore.LIGHTBLUE_EX}{total}{Fore.CYAN} items (Errors: {Fore.LIGHTRED_EX}{errors}{Fore.CYAN}){Style.RESET_ALL}", end='\r')
        return total, errors

    def scan_directory(self, path, file, progress_bar, prefix=''):
        try:
            items = os.listdir(path)
            for index, item in enumerate(items):
                item_path = os.path.join(path, item)
                is_last = index == len(items) - 1
                tree_prefix = '└── ' if is_last else '├── '
                new_prefix = '    ' if is_last else '│   '

                if os.path.isdir(item_path):
                    file.write(f"{prefix}{tree_prefix}{item}/\n")
                    self.scan_directory(item_path, file, progress_bar, prefix + new_prefix)
                else:
                    file.write(f"{prefix}{tree_prefix}{item}\n")
                progress_bar.update(1)

        except PermissionError as e:
            self.error_file.write(f"PermissionError accessing {path}: {e.strerror}\n")
            file.write(f"{prefix}└── Access Denied\n")
            progress_bar.update(1)

    @staticmethod
    def play_system_sound(no_beep):
        if not no_beep:
            ctypes.windll.user32.MessageBeep(0xFFFFFFFF)

    def run(self):
        if not self.args.path or not os.path.exists(self.args.path):
            print(f"{Fore.RED}Error: Invalid or non-existent path. Please specify a valid directory path.{Style.RESET_ALL}")
            return

        if not os.path.isdir(self.args.path):
            print(f"{Fore.RED}Error: The specified path is not a directory.{Style.RESET_ALL}")
            return

        if not self.args.output_file.endswith(".txt") or not self.is_valid_file_name(self.args.output_file):
            print(f"{Fore.RED}Error: Output file must have a .txt extension and a valid file name.{Style.RESET_ALL}")
            return

        if not self.args.error_log_file.endswith(".txt") or not self.is_valid_file_name(self.args.error_log_file):
            print(f"{Fore.RED}Error: Error log file must have a .txt extension and a valid file name.{Style.RESET_ALL}")
            return

        if not self.args.silent:
            init()  # Initialize colorama for colored text output
            print(f"{Fore.BLUE}Starting scan...{Style.RESET_ALL}")

        with open(self.args.error_log_file, 'w', encoding='utf-8') as self.error_file:
            total_items, errors = self.count_items(self.args.path)

            if not self.args.silent:
                print(f"\n{Fore.GREEN}Total items to scan: {Fore.LIGHTGREEN_EX}{total_items}{Style.RESET_ALL}")

            with open(self.args.output_file, 'w', encoding='utf-8') as file:
                with tqdm.tqdm(total=total_items, unit="item", disable=self.args.silent) as pbar:
                    self.scan_directory(self.args.path, file, pbar)

        if not self.args.silent:
            print(f"{Fore.GREEN}Scan completed!{Style.RESET_ALL}\n"
                  f"Structure saved in {Fore.LIGHTGREEN_EX}{self.args.output_file}{Style.RESET_ALL}\n"
                  f"Errors (if any) logged in {Fore.LIGHTGREEN_EX}{self.args.error_log_file}{Style.RESET_ALL}")
            self.play_system_sound(self.args.no_beep)
            deinit()  # Deinitialize colorama


def show_help():
    print(f"{Fore.LIGHTMAGENTA_EX}Tree Structure Creator{Style.RESET_ALL}\n"
          "Scan a directory and create a detailed structure report.\n\n"
          "Usage:\n"
          f"  {Fore.LIGHTGREEN_EX}python main.py {Fore.LIGHTCYAN_EX}--path <path> [--output_file <output_file>] [--error_log_file <error_log_file>] [--silent] [--no_beep]{Style.RESET_ALL}\n"
          f"  {Fore.LIGHTGREEN_EX}python main.py {Fore.LIGHTCYAN_EX}--gui{Style.RESET_ALL}\n\n"
          "Options:\n"
          f"  {Fore.LIGHTCYAN_EX}--path{Fore.WHITE}              Path of the directory to scan\n"
          f"  {Fore.LIGHTCYAN_EX}--output_file{Fore.WHITE}       File to save the scanned directory structure\n"
          f"  {Fore.LIGHTCYAN_EX}--error_log_file{Fore.WHITE}    File to log errors during scanning\n"
          f"  {Fore.LIGHTCYAN_EX}--silent{Fore.WHITE}            Run in silent mode (no prints or progress bar)\n"
          f"  {Fore.LIGHTCYAN_EX}--no_beep{Fore.WHITE}           Disable beep sound on completion\n"
          f"  {Fore.LIGHTCYAN_EX}--gui{Fore.WHITE}               Use GUI mode to enter parameters\n"
          f"  {Fore.LIGHTCYAN_EX}--help{Fore.WHITE}              Show this help message and exit\n\n"
          "Examples:\n"
          f"  {Fore.LIGHTGREEN_EX}python main.py {Fore.LIGHTCYAN_EX}--path \"C:\\Users\"{Style.RESET_ALL}\n"
          f"  {Fore.LIGHTGREEN_EX}python main.py {Fore.LIGHTCYAN_EX}--gui{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(
        add_help=False,
        description="Tree Structure Creator - Scan a directory and create a detailed structure report."
    )
    parser.add_argument("--path", help="Path of the directory to scan")
    parser.add_argument("--output_file", default="structure.txt", help="File to save the scanned directory structure")
    parser.add_argument("--error_log_file", default="error_log.txt", help="File to log errors during scanning")
    parser.add_argument("--silent", action="store_true", help="Run in silent mode (no prints or progress bar)")
    parser.add_argument("--no_beep", action="store_true", help="Disable beep sound on completion")
    parser.add_argument("--gui", action="store_true", help="Use GUI mode to enter parameters")
    parser.add_argument("--help", action="store_true", help="Show this help message and exit")

    args = parser.parse_args()

    if args.help:
        show_help()
        return

    if args.gui:
        print(f"\n{Fore.LIGHTMAGENTA_EX}{'*' * 60}\n{'*' + ' ' * 58 + '*'}\n*{'Welcome to the Tree Structure Creator!'.center(58)}*\n{'*' + ' ' * 58 + '*'}\n{'*' * 60}{Style.RESET_ALL}\n")
        print("-----------------------------------------")

        while True:
            args.path = input(f"{Fore.LIGHTCYAN_EX}Enter the directory path to scan:{Style.RESET_ALL}\n> ").strip()
            if os.path.isdir(args.path):
                break
            else:
                print(f"{Fore.RED}Error: The specified path is not a valid directory. Please try again.{Style.RESET_ALL}")

        default_output_file = "structure.txt"
        print(f"Default output file is '{default_output_file}'.")
        while True:
            args.output_file = input(f"{Fore.LIGHTCYAN_EX}Enter the name of the output file or press Enter to use default:{Style.RESET_ALL}\n> ").strip() or default_output_file
            if args.output_file.endswith(".txt") and TreeStructureCreator.is_valid_file_name(args.output_file):
                break
            else:
                print(f"{Fore.RED}Error: Output file must have a .txt extension and a valid file name. Please try again.{Style.RESET_ALL}")

        default_error_log_file = "error_log.txt"
        print(f"Default error log file is '{default_error_log_file}'.")
        while True:
            args.error_log_file = input(f"{Fore.LIGHTCYAN_EX}Enter the name of the error log file or press Enter to use default:{Style.RESET_ALL}\n> ").strip() or default_error_log_file
            if args.error_log_file.endswith(".txt") and TreeStructureCreator.is_valid_file_name(args.error_log_file):
                break
            else:
                print(f"{Fore.RED}Error: Error log file must have a .txt extension and a valid file name. Please try again.{Style.RESET_ALL}")

        print("Optional settings:")
        silent_input = input(f"{Fore.LIGHTCYAN_EX}Run in silent mode? (Yes/Y or No/N):{Style.RESET_ALL}\n> ").strip().lower()
        args.silent = silent_input in ["yes", "y"]

        no_beep_input = input(f"{Fore.LIGHTCYAN_EX}Disable beep sound on completion? (Yes/Y or No/N):{Style.RESET_ALL}\n> ").strip().lower()
        args.no_beep = no_beep_input in ["yes", "y"]

        print("-----------------------------------------")
        print(f"{Fore.GREEN}Configuration complete. Starting scan...{Style.RESET_ALL}")

    tree_creator = TreeStructureCreator(args)
    tree_creator.run()

if __name__ == "__main__":
    main()
