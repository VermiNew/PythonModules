import subprocess
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from rich.traceback import install
from colorama import Fore, Style, init
import logging

init(autoreset=True)
install()
logging.basicConfig(
    level=logging.INFO, format=f"{Fore.WHITE}%(asctime)s - %(levelname)s - %(message)s"
)


class PingPlotter:
    def __init__(self, target, packet_size=None, count=10, interval=1000):
        self.target = target
        self.packet_size = packet_size
        self.count = count
        self.interval = interval
        self.delays = []
        self.max_delay = 0
        self.current_ping = 0
        self.animation = None

    def update_plot(self, frame):
        if self.current_ping > self.count:
            while True:
                if (
                    input(
                        f"{Fore.LIGHTMAGENTA_EX}Do you want to close graph? (Y/N): {Style.RESET_ALL}\n{Fore.LIGHTCYAN_EX}> {Fore.LIGHTBLUE_EX}"
                    ).lower()
                    == "y"
                ):
                    plt.close(self.fig)
                    return

        packet_size_option = f"-l {self.packet_size}" if self.packet_size else ""
        command = f"ping -n 1 {packet_size_option} {self.target}"
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
            )
            output, errors = process.communicate()

            if errors:
                logging.error(f"{Fore.RED}Error:{Style.RESET_ALL} {errors}")
            else:
                delay = re.search(r"time=(\d+)ms", output)
                if delay:
                    delay_ms = int(delay.group(1))
                    self.delays.append(delay_ms)
                    if delay_ms > self.max_delay:
                        self.max_delay = delay_ms
                        self.ax.set_ylim(0, self.max_delay + 10)
                    self.line.set_data(range(len(self.delays)), self.delays)
                    percentage = (self.current_ping / self.count) * 100
                    logging.info(
                        f"{Fore.GREEN}Status:{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Working...{Style.RESET_ALL} "
                        f"{self.current_ping} / {self.count} {Fore.CYAN}(Progress: {percentage:.1f}%){Style.RESET_ALL}"
                    )
                else:
                    logging.warning(
                        f"{Fore.YELLOW}No delay found in ping response.{Style.RESET_ALL}"
                    )
        except Exception as e:
            logging.error(
                f"{Fore.RED}An error occurred during ping:{Style.RESET_ALL} {e}"
            )

        if len(self.delays) == self.count:
            average_delay = sum(self.delays) / len(self.delays)
            logging.info(
                f"{Fore.LIGHTBLUE_EX}Average: {Fore.LIGHTCYAN_EX}{average_delay:.2f} ms{Style.RESET_ALL}"
            )
            self.ax.axhline(
                y=average_delay,
                color="purple",
                linestyle="--",
                label=f"Average: {average_delay:.2f} ms",
                alpha=0.8,
            )
            self.ax.legend()
            self.fig.canvas.draw()

        self.current_ping += 1

    def plot_ping(self):
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(0, self.count)
        self.ax.set_ylim(0, 10)
        self.ax.set_title(f"Real-time ping delay to {self.target}")
        self.ax.set_xlabel("Ping number")
        self.ax.set_ylabel("Delay (ms)")
        (self.line,) = self.ax.plot([], [], label=f"Target: {self.target}", linewidth=4)
        self.ax.legend()
        self.ax.grid(True)

        self.animation = FuncAnimation(
            self.fig,
            self.update_plot,
            blit=False,
            interval=self.interval,
            cache_frame_data=False,
        )

        plt.show()


if __name__ == "__main__":
    while True:
        target = input(
            f"{Fore.GREEN}Please enter a target to ping (for example - google.com):{Style.RESET_ALL}\n{Fore.LIGHTCYAN_EX}> {Fore.LIGHTBLUE_EX}"
        )
        if not target.strip():
            logging.warning(
                f"{Fore.YELLOW}Target cannot be empty. Please enter a valid target. Example: google.com{Style.RESET_ALL}"
            )
        else:
            break

    while True:
        packet_size_input = input(
            f"{Fore.GREEN}Enter packet size in bytes or leave empty for automatic:{Style.RESET_ALL}\n{Fore.LIGHTCYAN_EX}> {Fore.LIGHTBLUE_EX}"
        ).strip()
        if packet_size_input.isdigit() or not packet_size_input:
            packet_size = (
                int(packet_size_input) if packet_size_input.isdigit() else None
            )
            break
        else:
            logging.warning(
                f"{Fore.YELLOW}Please enter a valid packet size (number) or leave it empty for automatic size.{Style.RESET_ALL}"
            )

    while True:
        count_input = input(
            f"{Fore.GREEN}Enter the number of pings (default 10):{Style.RESET_ALL}\n{Fore.LIGHTCYAN_EX}> {Fore.LIGHTBLUE_EX}"
        ).strip()
        if count_input.isdigit() or not count_input:
            count = int(count_input) if count_input else 10
            break
        else:
            logging.warning(
                f"{Fore.YELLOW}Please enter a valid number of pings or leave it empty for default (10).{Style.RESET_ALL}"
            )

    while True:
        interval_input = input(
            f"{Fore.GREEN}Enter the interval between pings in milliseconds (default 1000):{Style.RESET_ALL}\n{Fore.LIGHTCYAN_EX}> {Fore.LIGHTBLUE_EX}"
        ).strip()
        if interval_input.isdigit() or not interval_input:
            interval = int(interval_input) if interval_input else 1000
            break
        else:
            logging.warning(
                f"{Fore.YELLOW}Please enter a valid interval (number in milliseconds) or leave it empty for default (1000 ms).{Style.RESET_ALL}"
            )

    if target:
        logging.info(f"{Fore.GREEN}Starting plotter...{Style.RESET_ALL}")
        plotter = PingPlotter(target, packet_size, count, interval)
        plotter.plot_ping()
    else:
        logging.warning(
            f"{Fore.YELLOW}Target cannot be empty. Please enter a valid target.{Style.RESET_ALL}"
        )
