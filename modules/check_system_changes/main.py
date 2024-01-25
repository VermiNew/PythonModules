import os
import argparse
import threading
import time
from datetime import datetime
from colorama import init, Fore, Style
from tkinter import Tk, Label, Entry, Button, StringVar, filedialog, messagebox, Checkbutton

class FileChecker:
    def __init__(self):
        init()  # Initialize colorama
        self.found_files = []
        self.iteration = 0
        self.running = False

    def is_date_compatible(self, date1, date2):
        return date1 == date2

    def is_date_time_compatible(self, datetime1, datetime2):
        return datetime1 >= datetime2

    def parse_date(self, date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    def parse_time(self, time_str):
        return datetime.strptime(time_str, "%H:%M").time()

    def check_changes(self, directory_path, target_date, target_time=None, output_file=None, debug=False, show_skipped=False):
        self.found_files = []
        self.running = True
        try:
            # Print information about the File Changes Checker
            print(f"{Fore.CYAN}File Changes Checker{Style.RESET_ALL}")
            print("\nParameters:")
            print(f"  {Fore.YELLOW}Path:{Style.RESET_ALL} {directory_path}")
            print(f"  {Fore.YELLOW}Date:{Style.RESET_ALL} {target_date}")
            if target_time:
                print(f"  {Fore.YELLOW}Time:{Style.RESET_ALL} {target_time}")
            print(f"  {Fore.YELLOW}Output:{Style.RESET_ALL} {output_file}")
            print(f"  {Fore.YELLOW}Debug:{Style.RESET_ALL} {debug}")
            print(f"  {Fore.YELLOW}Show Skipped:{Style.RESET_ALL} {show_skipped}\n")

            if debug:
                print(f"{Fore.GREEN}Debug mode enabled. Working...{Style.RESET_ALL}")

            # Traverse the directory and check for file changes
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    if not self.running:
                        break  # Stop the search if the user cancels
                    file_path = os.path.join(root, file)
                    last_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    # Check if the file's date and time match the target
                    if self.is_date_compatible(last_modified_time.date(), target_date):
                        if target_time:
                            target_datetime = datetime.combine(target_date, target_time)
                            if self.is_date_time_compatible(last_modified_time, target_datetime):
                                self.found_files.append((file_path, last_modified_time))
                                # Display in real-time with different colors
                                print(f"{Fore.GREEN}Found: {Fore.LIGHTGREEN_EX}{file_path} {Fore.LIGHTWHITE_EX}({last_modified_time})" + Style.RESET_ALL)
                        else:
                            self.found_files.append((file_path, last_modified_time))
                            # Display in real-time with different colors
                            print(f"{Fore.GREEN}Found: {Fore.CYAN}{file_path} {Fore.LIGHTCYAN_EX}({last_modified_time})" + Style.RESET_ALL)
                    elif show_skipped:
                        print(f"{Fore.MAGENTA}Skipped: {Fore.LIGHTMAGENTA_EX}{file_path} {Fore.LIGHTWHITE_EX}(Last Modified: {last_modified_time})" + Style.RESET_ALL)

                    # Display iteration in debug mode
                    if debug:
                        self.iteration += 1
                        print(f"{Fore.CYAN}Scanned: {Fore.LIGHTBLUE_EX}{self.iteration}{Style.RESET_ALL}", end="\r")

            # Print results after checking changes
            if self.found_files:
                print("\nFound changes in the following files:")
                for file_path, last_modified_time in self.found_files:
                    print(f"{Fore.YELLOW}Found: {Fore.LIGHTYELLOW_EX}{file_path} {Fore.LIGHTWHITE_EX}({last_modified_time})" + Style.RESET_ALL)

                # Save information to a file at the end
                if output_file:
                    with open(output_file, "a") as file:
                        file.write(f"\nParameters:\n")
                        file.write(f"  Path: {directory_path}\n")
                        file.write(f"  Date: {target_date}\n")
                        if target_time:
                            file.write(f"  Time: {target_time}\n")
                        file.write(f"  Output: {output_file}\n")
                        file.write(f"  Debug: {debug}\n")
                        file.write(f"  Show Skipped: {show_skipped}\n\n")

                        file.write("Found changes in the following files:\n")
                        file.write("\n".join([f"Found: {file_path} ({last_modified_time})" for file_path, last_modified_time in self.found_files]))
                        file.write("\n")

            else:
                print(Fore.BLUE + "\nNo changes found." + Style.RESET_ALL)

            print(Fore.MAGENTA + "\nFinished checking changes." + Style.RESET_ALL)

        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nSearch canceled by the user." + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + "An error occurred:", e, Style.RESET_ALL)
        finally:
            self.running = False

class GUI:
    def __init__(self, root, file_checker):
        self.root = root
        self.root.title("File Changes Checker")
        self.file_checker = file_checker

        # GUI elements
        self.directory_label = Label(root, text="Directory Path:")
        self.directory_label.pack()

        self.directory_entry = Entry(root)
        self.directory_entry.pack()

        self.date_label = Label(root, text="Date (YYYY-MM-DD):")
        self.date_label.pack()

        self.date_entry = Entry(root)
        self.date_entry.pack()

        self.time_label = Label(root, text="Time (optional, HH:MM):")
        self.time_label.pack()

        self.time_entry = Entry(root)
        self.time_entry.pack()

        self.output_label = Label(root, text="Output File (optional):")
        self.output_label.pack()

        self.output_entry = Entry(root)
        self.output_entry.insert(0, "output.txt")
        self.output_entry.pack()

        self.skipped_var = StringVar()
        self.skipped_var.set("0")
        self.skipped_checkbox = Checkbutton(root, text="Show Skipped", variable=self.skipped_var, onvalue="1", offvalue="0")
        self.skipped_checkbox.pack()

        self.check_button = Button(root, text="Check Changes", command=self.check_changes)
        self.check_button.pack()

    def check_changes(self):
        # Get input from GUI elements and initiate file checking
        directory_path = self.directory_entry.get()
        target_date_str = self.date_entry.get()
        target_time_str = self.time_entry.get()
        output_file = self.output_entry.get()
        show_skipped = self.skipped_var.get() == "1"

        try:
            target_date = self.file_checker.parse_date(target_date_str)
            target_time = self.file_checker.parse_time(target_time_str) if target_time_str else None

            # Check if file checking is already in progress
            if not self.file_checker.running:
                self.file_checker_thread = threading.Thread(target=self.file_checker.check_changes, args=(directory_path, target_date, target_time, output_file, False, show_skipped))
                self.file_checker_thread.start()
                self.root.after(100, self.check_thread_status)  # Check the thread status every 100 milliseconds
            else:
                messagebox.showinfo("Info", "Checking changes is already in progress.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def check_thread_status(self):
        # Check the status of the file checker thread
        if self.file_checker_thread.is_alive():
            self.root.after(100, self.check_thread_status)
        else:
            messagebox.showinfo("Finished", "Finished checking changes.")

def print_help_and_exit():
    # Print help information and exit
    print("\nFile Changes Checker\n")
    print(f"{Fore.CYAN}Options:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}--path{Style.RESET_ALL}         Path to the directory to check {Fore.RED}(required){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}--date{Style.RESET_ALL}         Date to check for changes (YYYY-MM-DD) {Fore.RED}(required){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}--time{Style.RESET_ALL}         Time to check for changes (HH:MM) {Fore.RED}(optional){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}--output{Style.RESET_ALL}       Output file path {Fore.RED}(optional, default: output.txt){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}--debug{Style.RESET_ALL}        Enable debug mode {Fore.RED}(optional){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}--show-skipped{Style.RESET_ALL} Show skipped files during checking {Fore.RED}(optional){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}--gui{Style.RESET_ALL}          Run in GUI mode {Fore.RED}(optional){Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}Examples:{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}main.py --path <directory_path> --date <YYYY-MM-DD> [--time <HH:MM>] [--output <output_file>] [--debug] [--show-skipped]{Style.RESET_ALL}")
    print(f"  {Fore.GREEN}main.py --gui{Style.RESET_ALL}\n")
    print(f"{Fore.CYAN}Notes:{Style.RESET_ALL}")
    print(f"- When using GUI mode, other command-line options are not required.")
    print(f"- If {Fore.YELLOW}--output{Style.RESET_ALL} is not specified, the default output file is {Fore.GREEN}'output.txt'{Style.RESET_ALL}.\n")
    exit()

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='File Changes Checker')
        parser.add_argument('--path', help='Path to the directory to check')
        parser.add_argument('--date', help='Date to check for changes (YYYY-MM-DD)')
        parser.add_argument('--time', help='Time to check for changes (HH:MM)')
        parser.add_argument('--output', help='Output file path')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode')
        parser.add_argument('--show-skipped', action='store_true', help='Show skipped files during checking')
        parser.add_argument('--gui', action='store_true', help='Run in GUI mode')
        args = parser.parse_args()

        if args.gui:
            # Run in GUI mode
            root = Tk()
            file_checker = FileChecker()
            gui = GUI(root, file_checker)
            root.protocol("WM_DELETE_WINDOW", lambda: file_checker.running or root.destroy())
            root.resizable(False, False)
            root.mainloop()
        else:
            # Run in command-line mode
            if args.path is None or args.date is None:
                print_help_and_exit()

            output_file = args.output if args.output else "output.txt"
            checker = FileChecker()
            checker.check_changes(args.path, args.date, args.time, output_file, args.debug, args.show_skipped)

    except Exception as e:
        print(Fore.RED + "An unexpected error occurred:", e, Style.RESET_ALL)
