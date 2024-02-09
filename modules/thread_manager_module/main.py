import time
import random
from colorama import Fore, Style, init
from rich.console import Console
from rich.traceback import install
from thread_manager import ThreadManager

# Initialize colorama and rich for console styling
init(autoreset=True)
install()

console = Console()

def AVG_Function(iterations, thread_id, timer):
    try:
        # Generate random values for the specified number of iterations
        values = [random.randint(1, 100) for _ in range(iterations)]
        for i, value in enumerate(values):
            # Update the progress in the description label
            progress = (i + 1) / iterations * 100
            thread_manager.threads[thread_id].update_description(f"Progress: {progress:.2f}%")
            time.sleep(timer)

        # Calculate and print the average
        average = sum(values) / iterations
        print(f"Average for Thread {thread_id}: {average:.2f}")
    except Exception as e:
        # Handle exceptions and print an error message
        print(Fore.RED + f"Error in AVG_Function for Thread {thread_id}: {e}" + Style.RESET_ALL)
        console.print_exception(show_locals=True)

# Create an instance of ThreadManager
try:
    thread_manager = ThreadManager(num_threads=16, x_position=0, y_position=10)

    # Start jobs for two threads
    thread_manager.start_job(0, lambda: AVG_Function(100, 0, 0.03), description="Calculating average for Thread 0")
    thread_manager.start_job(1, lambda: AVG_Function(100, 1, 0.01), description="Calculating average for Thread 1")

    # Start the Tkinter GUI main loop
    thread_manager.start_gui()
except KeyboardInterrupt:
    pass  
except Exception as e:
    print(e)
    console.print_exception(show_locals=True)
finally:
    try:
        # Close the Tkinter GUI
        thread_manager.deinit()
        # Cleanup
        thread_manager.cleanup()
    except Exception as e:
        print(e)
        console.print_exception(show_locals=True)
