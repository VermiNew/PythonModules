import argparse
import tkinter as tk
from tkinter import ttk, messagebox
import ipinfo
import re
import shutil
import sys
import time
import pyperclip
from geopy.geocoders import Nominatim
from colorama import Style, Fore, init
import threading
from rich.logging import RichHandler
import logging

init(autoreset=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("rich")


def parse_args():
    parser = argparse.ArgumentParser(
        description="MapperApp: A tool for mapping IP addresses."
    )
    parser.add_argument("--ip", help="IP address to map.")
    parser.add_argument("--token", help="Access token for the IPinfo API.")
    parser.add_argument("--debug", action="store_true", help="Activate debug mode.")

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    return args


class MapperAppGUI:
    def __init__(self, master, cmd_args=None):
        self.master = master
        self.cmd_args = cmd_args
        self.master.title("Enter IP Address and Access Token")

        if cmd_args and cmd_args.ip and cmd_args.token:
            MapperApp(cmd_args.ip, cmd_args.token)
        else:
            self.init_window()
            self.create_widgets_ip()

    def init_window(self):
        window_width = 400
        window_height = 150
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2 - 10)
        center_y = int(screen_height / 2 - window_height / 2 - 20)
        self.master.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
        self.master.resizable(False, False)

    def create_widgets_ip(self):
        ttk.Label(self.master, text="Enter the IP address:").pack(pady=10)
        self.ip_entry = ttk.Entry(self.master, width=30)
        self.ip_entry.pack(pady=5)
        self.ip_entry.focus()

        submit_button = ttk.Button(self.master, text="Next", command=self.on_submit_ip)
        submit_button.pack(pady=10)

    def on_submit_ip(self):
        ip_address = self.ip_entry.get()
        if self.validate_ip(ip_address):
            self.ip_address = ip_address
            self.create_widgets_token()
        else:
            messagebox.showerror(
                "Error", "An invalid IP address has been entered. Please try again."
            )

    def create_widgets_token(self):
        for widget in self.master.winfo_children():
            widget.destroy()

        ttk.Label(self.master, text="Enter the Access Token:").pack(pady=10)
        self.token_entry = ttk.Entry(self.master, width=30)
        self.token_entry.pack(pady=5)
        self.token_entry.focus()

        token_link_button = ttk.Button(
            self.master,
            text="Copy link to IPinfo page to acquire token",
            command=self.copy_token_link,
        )
        token_link_button.pack(pady=5)

        submit_button = ttk.Button(self.master, text="OK", command=self.on_submit_token)
        submit_button.pack(pady=10)

    def copy_token_link(self):
        token_link = "https://ipinfo.io/account/token"
        pyperclip.copy(token_link)
        messagebox.showinfo(
            "Successfully copied", "The link to the token was copied to the clipboard."
        )

    def on_submit_token(self):
        token = self.token_entry.get()
        if token:
            self.master.destroy()
            MapperApp(self.ip_address, token)
        else:
            messagebox.showerror(
                "Error", "The access token must not be empty. Please try again."
            )

    def validate_ip(self, ip):
        pattern_ipv4 = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        pattern_ipv6 = r"(\A(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\Z)|(\A(?:[0-9a-fA-F]{1,4}:){1,7}:\Z)|(\A(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}\Z)|(\A(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}\Z)|(\A(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}\Z)|(\A(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}\Z)|(\A(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}\Z)|(\A[0-9a-fA-F]{1,4}:(?::[0-9a-fA-F]{1,4}){1,6}\Z)|(\A:(?::[0-9a-fA-F]{1,4}){1,7}\Z)|(\A::\Z)|(\A:(?::[0-9a-fA-F]{1,4}){1,7}\Z)"

        if re.match(pattern_ipv4, ip) or re.match(pattern_ipv6, ip):
            return True
        return False

    def start_mapper_app(self, ip_address):
        MapperApp(ip_address)

    def close_window(self):
        self.master.destroy()


class MapperApp:
    def __init__(self, ip_address, access_token):
        self.ip_address = ip_address
        self.access_token = access_token
        try:
            self.handler = ipinfo.getHandler(self.access_token)
        except Exception as e:
            logger.error("IPInfo handler cannot be initialized: ", exc_info=e)
            sys.exit(1)
        try:
            self.geolocator = Nominatim(user_agent="geoapiExercises")
        except Exception as e:
            logger.error("The GeoPy handler cannot be initialized: ", exc_info=e)

        threading.Thread(target=self.main).start()

    def get_all_ip_info(self):
        try:
            details = self.handler.getDetails(self.ip_address)
            return details.all
        except Exception as e:
            logger.error("Unable to download IP information: ", exc_info=e)
            return {}

    def split_loc_to_lat_long(self, data):
        output = {}
        if "loc" in data:
            latitude, longitude = data["loc"].split(",")
            output["latitude"] = latitude.strip()
            output["longitude"] = longitude.strip()
        return output

    def get_detailed_address_from_ip_info(self, info, attempts=3, delay=10):
        for attempt in range(1, attempts + 1):
            data = self.split_loc_to_lat_long(info)
            location = None

            try:
                builded_string = f'{data["latitude"]}, {data["longitude"]}'
                location = self.geolocator.reverse(builded_string)
                if location:
                    return location.address
                else:
                    raise Exception(
                        "The address for the specified location cannot be found."
                    )
            except Exception as e:
                if "403" in str(e):
                    logger.warning(
                        f"Non-successful status code 403. Attempt {attempt} of {attempts}."
                    )
                    logger.info("Waiting for reconnection...")

                    for remaining in range(delay, 0, -1):
                        sys.stdout.write(
                            f"\r{Fore.GREEN}Remaining: {remaining} seconds{Style.RESET_ALL}"
                            + " " * 10
                        )
                        sys.stdout.flush()
                        time.sleep(1)

                    print()
                else:
                    logger.error(
                        "An error occurred while obtaining the detailed address!",
                        exc_info=e,
                    )
                    return (
                        "An error occurred while processing the IP address information."
                    )
        return "The limit of attempts to process the IP address information has been exceeded."

    def center_text(self, text, terminal_width):
        try:
            color_regex = re.compile(r"\x1b\[[0-9;]*m")
            stripped_text = color_regex.sub("", text)

            padding = (terminal_width - len(stripped_text)) // 2
            print(" " * padding + text)
        except Exception as e:
            logger.error(f"An error occurred while centering the text: {e}")

    def main(self):
        terminal_width = shutil.get_terminal_size().columns
        info = self.get_all_ip_info()
        print(f"{Fore.LIGHTBLACK_EX}" + "-" * terminal_width + f"{Style.RESET_ALL}")

        try:
            for key, value in info.items():
                print(
                    f"{Fore.LIGHTCYAN_EX}{key.upper():30}{Style.RESET_ALL}",
                    f"{Fore.LIGHTBLACK_EX}:{Style.RESET_ALL} ",
                    f"{Fore.CYAN}{value}{Style.RESET_ALL}",
                )
        except Exception as e:
            logger.error("An error occurred while displaying data: ", exc_info=e)

        print(f"{Fore.LIGHTBLACK_EX}" + "-" * terminal_width + f"{Style.RESET_ALL}")
        detailed_address = self.get_detailed_address_from_ip_info(info)

        self.center_text(
            f"{Fore.LIGHTCYAN_EX}Address based on geolocation data:{Style.RESET_ALL}",
            terminal_width,
        )
        self.center_text(
            f"{Fore.CYAN}{detailed_address}{Style.RESET_ALL}", terminal_width
        )


if __name__ == "__main__":
    args = parse_args()
    root = tk.Tk()
    app_gui = MapperAppGUI(root, cmd_args=args)
    root.mainloop()
