import time
from colorama import Style, Fore, init
from ppbm import ProgressBar
from rich.traceback import install

init(autoreset=True)
install()

if __name__ == "__main__":
    try:
        total_steps = 100
        long_task_description = "Processing..."

        progress_bar = ProgressBar(total_steps, task=long_task_description, color=Fore.CYAN)

        for _ in range(total_steps):
            time.sleep(0.1) 
            progress_bar.update()

    except Exception as e:
        print(f"{Fore.RED}An error occurred in the main block: {e}{Style.RESET_ALL}")
