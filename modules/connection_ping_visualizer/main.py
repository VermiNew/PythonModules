import subprocess
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from rich.traceback import install
from colorama import Fore, Style, init

init(autoreset=True)
install()


class PingPlotter:
    def __init__(self, target, count=250):
        """Initialize the PingPlotter with a target host and count of pings."""
        self.target = target
        self.count = count
        self.delays = []

    def update_plot(self, frame):
        """Ping the target once and update the plot with the new delay."""
        print(
            f"{Fore.LIGHTCYAN_EX}Pinging {Fore.LIGHTBLUE_EX}{self.target}{Fore.LIGHTCYAN_EX}...{Style.RESET_ALL}"
        )
        command = f"ping -n 1 {self.target}"
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
        )
        output, errors = process.communicate()

        if errors:
            print(f"{Fore.RED}Error: {errors}")
        else:
            delay = re.search(r"time=(\d+)ms", output)
            if delay:
                delay_ms = int(delay.group(1))
                self.delays.append(delay_ms)
                self.line.set_data(range(len(self.delays)), self.delays)
                print(
                    f"{Fore.LIGHTCYAN_EX}Delay: {Fore.LIGHTBLUE_EX}{delay_ms} ms{Fore.LIGHTCYAN_EX} added to plot{Style.RESET_ALL}"
                )

    def plot_ping(self):
        """Setup the plot and start animating the ping results in real-time."""
        fig, ax = plt.subplots()
        ax.set_xlim(0, self.count)
        
        if self.delays:
            ax.set_ylim(0, max(self.delays) + 50)
        else:
            ax.set_ylim(0, 100)

        
        ax.set_title(f"Real-time ping delay to {self.target}")
        ax.set_xlabel("Ping number")
        ax.set_ylabel("Delay (ms)")
        (self.line,) = ax.plot([], [], label=f"Delay in ms to {self.target}")
        ax.legend()
        ax.grid(True)

        ani = FuncAnimation(
            fig, self.update_plot, frames=range(self.count), blit=False, interval=200
        )
        
        plt.show()


if __name__ == "__main__":
    while True:
        target = input(
            f"{Fore.GREEN}Please enter a target to ping (for example - google.com): {Style.RESET_ALL}\n{Fore.LIGHTCYAN_EX}> {Style.RESET_ALL}"
        )
        if target:
            try:
                plotter = PingPlotter(target)
                plotter.plot_ping()
                break
            except Exception as e:
                print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        else:
            print(
                f"{Fore.YELLOW}Target cannot be empty. Please enter a valid target.{Style.RESET_ALL}"
            )
    print(f"{Fore.LIGHTBLUE_EX}Completed!{Style.RESET_ALL}")
