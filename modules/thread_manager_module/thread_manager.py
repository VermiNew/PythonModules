import tkinter as tk
import threading
import os
import sys
from colorama import Fore, Style, init
from rich.console import Console
from rich.traceback import install

# Initialize colorama and rich for console styling
init(autoreset=True)
install()

console = Console()

class JobThread(threading.Thread):
    def __init__(self, thread_id, thread_manager, job_func, label, status_label, description_label):
        super().__init__()
        self.thread_id = thread_id
        self.thread_manager = thread_manager
        self.job_func = job_func
        self.label = label
        self.status_label = status_label
        self.description_label = description_label
        self.description = "No description"

    def run(self):
        try:
            # Configure labels and update thread status
            self.label.config(bg="green")
            self.status_label.config(text="Running", anchor="w")
            self.update_description("")  
            self.job_func()
            self.label.config(bg="gray")
            self.status_label.config(text="Ready", anchor="w")
            self.update_description("")  

            # Remove the thread from the manager after completion
            self.thread_manager.remove_thread(self.thread_id)

            # Create a new instance of the thread and add it back to the manager
            new_thread = JobThread(self.thread_id, self.thread_manager, self.job_func, self.label, self.status_label, self.description_label)
            self.thread_manager.threads[self.thread_id] = new_thread
            self.thread_manager.thread_labels[self.thread_id] = self.label
        except Exception as e:
            console.print_exception(show_locals=True)

    def update_description(self, new_description):
        # Update the description label with new text
        self.description = new_description
        self.description_label.after(0, self.description_label.config, {'text': self.description, 'anchor': 'w'})

class ThreadManager:
    def __init__(self, num_threads, x_position, y_position):
        try:
            # Initialize Tkinter root window
            self.root = tk.Tk()
            self.root.title("Thread Monitor")
            self.root.geometry(f"400x400+{x_position}+{y_position}")
            self.root.resizable(width=True, height=False)  

            # Configure grid layout
            self.root.grid_rowconfigure(0, weight=1)
            self.root.grid_columnconfigure(0, weight=1)

            # Create a frame for labels
            frame = tk.Frame(self.root)
            frame.grid(row=0, column=0, sticky="nsew")

            self.threads = []
            self.thread_labels = []

            # Create labels for each thread
            for i in range(num_threads):
                label_text = f"Thread {i:02d}"
                label = tk.Label(frame, text=label_text, padx=5, anchor="w", bg="gray")
                label.grid(row=i, column=0, pady=2, sticky="w")

                status_label = tk.Label(frame, text="Ready", padx=5, anchor="w")
                status_label.grid(row=i, column=1, pady=2, sticky="w")

                description_label = tk.Label(frame, text="", padx=5, anchor="w")
                description_label.grid(row=i, column=2, pady=2, sticky="w")

                thread = JobThread(i, self, None, label, status_label, description_label)
                self.threads.append(thread)
                self.thread_labels.append(label)
        except Exception as e:
            console.print_exception(show_locals=True)

    def start_job(self, thread_id, job_func, description="No description"):
        try:
            # Start a job for the specified thread
            thread = self.threads[thread_id]
            thread.job_func = job_func
            thread.update_description(description)
            if not thread.is_alive():
                thread.start()
        except Exception as e:
            console.print_exception(show_locals=True)

    def remove_thread(self, thread_id):
        try:
            # Remove a thread from the manager
            if thread_id < len(self.threads):
                del self.threads[thread_id]
                del self.thread_labels[thread_id]
        except Exception as e:
            console.print_exception(show_locals=True)

    def start_gui(self):
        try:
            # Start the Tkinter GUI main loop
            self.root.resizable(width=True, height=False)
            self.root.protocol("WM_DELETE_WINDOW", lambda: sys.exit())
            self.root.mainloop()
        except KeyboardInterrupt:
            self.deinit()
            sys.exit()
        except Exception as e:
            console.print_exception(show_locals=True)

    def deinit(self):
        try:
            # Destroy the Tkinter root window
            self.root.destroy()
        except Exception as e:
            console.print_exception(show_locals=True)

    def close_gui(self):
        try:
            # Quit the Tkinter GUI
            self.root.quit()
        except Exception as e:
            console.print_exception(show_locals=True)

    def cleanup(self):
        print(Fore.CYAN + "Cleaning up..." + Style.RESET_ALL)
        os.system("rmdir /s /q __pycache__")
        print(Fore.CYAN + "Cleaned!" + Style.RESET_ALL)
        sys.exit()

    def help(self):
        # Display help information for the ThreadManager class
        print(Fore.BLUE + "ThreadManager Class:")
        print(Fore.CYAN + "1. __init__(num_threads, x_position, y_position): Initializes the ThreadManager.")
        print("   - num_threads: Number of threads to manage.")
        print("   - x_position, y_position: Initial position of the Tkinter window.")
        print(Fore.CYAN + "2. start_job(thread_id, job_func, description='No description'): Starts a job for the specified thread.")
        print("   - thread_id: ID of the thread to start the job.")
        print("   - job_func: Function to be executed as the job.")
        print("   - description: Description of the job (default is 'No description').")
        print(Fore.CYAN + "3. start_gui(): Starts the Tkinter GUI main loop.")
        print(Fore.CYAN + "4. close_gui(): Closes/destroys the Tkinter GUI." + Style.RESET_ALL)
