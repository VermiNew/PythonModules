import subprocess
import re
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from rich.traceback import install
from colorama import Fore, Style, init
from tkinter import Tk, Label, Entry, Button, StringVar, messagebox
import tkinter.scrolledtext as ScrolledText
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
                        f"{Fore.LIGHTMAGENTA_EX}Do you want to close graph? "
                        f"({Fore.LIGHTYELLOW_EX}Y{Fore.LIGHTMAGENTA_EX} to close):"
                        f"{Style.RESET_ALL}\n{Fore.LIGHTCYAN_EX}> {Fore.LIGHTBLUE_EX}"
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
                        f"{Fore.LIGHTBLACK_EX}Status:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}Working...{Style.RESET_ALL} "
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


class GUI_TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.config(state="disabled")

    def emit(self, record):
        msg = self.format(record)
        msg_clean = re.sub(r"\x1b\[[0-9;]*m", "", msg)
        self.text_widget.config(state="normal")
        self.text_widget.insert("end", msg_clean + "\n")
        self.text_widget.config(state="disabled")
        self.text_widget.yview("end")


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Connection Ping Visualizer")
        master.resizable(0, 0)

        self.init_gui_elements()

    def init_gui_elements(self):
        Label(self.master, text="Target (for example, google.com):").grid(
            row=0, sticky="W"
        )
        self.target_var = StringVar()
        Entry(self.master, textvariable=self.target_var).grid(row=0, column=1)

        Label(self.master, text="Packet size in bytes (optional):").grid(
            row=1, sticky="W"
        )
        self.packet_size_var = StringVar()
        Entry(self.master, textvariable=self.packet_size_var).grid(row=1, column=1)

        Label(self.master, text="Number of pings (default 10):").grid(row=2, sticky="W")
        self.count_var = StringVar()
        Entry(self.master, textvariable=self.count_var).grid(row=2, column=1)

        Label(self.master, text="Interval in milliseconds (default 1000):").grid(
            row=3, sticky="W"
        )
        self.interval_var = StringVar()
        Entry(self.master, textvariable=self.interval_var).grid(row=3, column=1)

        self.log_text = ScrolledText.ScrolledText(
            self.master, state="disabled", height=10
        )
        self.log_text.grid(row=5, columnspan=2)

        Button(self.master, text="Start", command=self.execute_ping).grid(
            row=4, columnspan=2
        )

        self.setup_logging()

    def setup_logging(self):
        text_handler = GUI_TextHandler(self.log_text)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        text_handler.setFormatter(formatter)
        logging.getLogger().addHandler(text_handler)
        logging.getLogger().setLevel(logging.INFO)

    def execute_ping(self):
        target = self.target_var.get()
        packet_size_input = self.packet_size_var.get()
        count_input = self.count_var.get()
        interval_input = self.interval_var.get()

        if not target:
            messagebox.showerror(
                "Error", "Target cannot be empty. Please enter a valid target."
            )
            logging.error(
                f"{Fore.RED}Target cannot be empty. Please enter a valid target.{Style.RESET_ALL}"
            )
            return

        try:
            packet_size = int(packet_size_input) if packet_size_input else None
        except ValueError:
            messagebox.showerror(
                "Error",
                "Packet size must be an integer or left empty for the default value.",
            )
            logging.error(
                f"{Fore.RED}Packet size must be an integer or left empty for the default value.{Style.RESET_ALL}"
            )
            return

        try:
            count = int(count_input) if count_input else 10
        except ValueError:
            messagebox.showerror("Error", "Number of pings must be an integer.")
            logging.error(
                f"{Fore.RED}Number of pings must be an integer or left empty for the default value.{Style.RESET_ALL}"
            )
            return

        try:
            interval = int(interval_input) if interval_input else 1000
        except ValueError:
            messagebox.showerror(
                "Error", "Interval must be an integer expressed in milliseconds."
            )
            logging.error(
                f"{Fore.RED}Interval must be an integer expressed in milliseconds or left empty for the default value.{Style.RESET_ALL}"
            )
            return

        logging.info(f"{Fore.LIGHTGREEN_EX}Starting plotter...{Style.RESET_ALL}")
        plotter = PingPlotter(target, packet_size, count, interval)
        plotter.plot_ping()


if __name__ == "__main__":
    root = Tk()
    my_gui = GUI(root)
    root.mainloop()
