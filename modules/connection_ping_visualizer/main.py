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
        self.average_line = None
        self.animation = None

    def update_plot(self, frame):
        if self.current_ping > self.count:
            logging.info(f"{Fore.GREEN}Operation has ended!{Style.RESET_ALL}")
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
                    if percentage < 100 and percentage is not None:
                        self.ax.set_xlabel(f"Progress: {percentage:.1f}%")
                    else:
                        self.ax.set_xlabel("Ping number")
                else:
                    logging.warning(
                        f"{Fore.YELLOW}No delay found in ping response.{Style.RESET_ALL}"
                    )
        except Exception as e:
            logging.error(
                f"{Fore.RED}An error occurred during ping:{Style.RESET_ALL} {e}"
            )

        if len(self.delays) > 0:
            average_delay = sum(self.delays) / len(self.delays)

            if len(self.delays) == self.count + 1 and average_delay is not None:
                logging.info(
                    f"{Fore.LIGHTBLUE_EX}Average: {Fore.LIGHTCYAN_EX}{average_delay:.2f} ms{Style.RESET_ALL}"
                )

            if self.average_line is not None:
                self.average_line.remove()

            self.average_line = self.ax.axhline(
                y=average_delay,
                color="purple",
                linestyle="--",
                label=f"Average: {average_delay:.2f} ms",
                alpha=0.8,
            )
            self.ax.legend()

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

        try:
            root = plt.get_current_fig_manager().window
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.update_idletasks()

            window_width = root.winfo_reqwidth()
            window_height = root.winfo_reqheight()

            position_right = int((screen_width / 2) - (window_width / 2)) - 20
            position_down = int((screen_height / 2) - (window_height / 2)) - 20

            root.geometry(f"+{position_right}+{position_down}")
            logging.info(
                f"{Fore.GREEN}Centered the graph window successfully.{Style.RESET_ALL}"
            )
        except Exception as e:
            logging.error(
                f"{Fore.RED}Error centering graph window: {e}{Style.RESET_ALL}"
            )

        logging.info(f"{Fore.LIGHTBLACK_EX}Starting animation...{Style.RESET_ALL}")

        self.animation = FuncAnimation(
            self.fig,
            self.update_plot,
            blit=False,
            interval=self.interval,
            repeat=False,
            frames=self.count,
            cache_frame_data=False,
        )

        try:
            plt.show()
        except Exception as e:
            logging.error(
                f"{Fore.RED}Error displaying graph window: {e}{Style.RESET_ALL}"
            )


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
        self.center_window()

    def center_window(self):
        try:
            self.master.update_idletasks()
            width = self.master.winfo_width()
            height = self.master.winfo_height()
            screen_width = self.master.winfo_screenwidth()
            screen_height = self.master.winfo_screenheight()
            x = int((screen_width / 2) - (width / 2)) - 20
            y = int((screen_height / 2) - (height / 2)) - 20
            self.master.geometry(f"{width}x{height}+{x}+{y}")
            logging.info(
                f"{Fore.GREEN}Centered the window successfully.{Style.RESET_ALL}"
            )
        except Exception as e:
            logging.error(f"{Fore.RED}Error centering the window: {e}{Style.RESET_ALL}")

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
