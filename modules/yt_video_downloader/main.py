import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import os
import threading
from moviepy.editor import VideoFileClip
import logging
from colorama import Fore, Style, init
from rich.traceback import install

init(autoreset=True)
install()


class TextHandler(logging.Handler):
    def __init__(self, text):
        super().__init__()
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        # Remove Colorama color sequences using a regular expression
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        msg = ansi_escape.sub("", msg)

        self.text.configure(state="normal")
        self.text.insert(tk.END, msg + "\n")
        self.text.configure(state="disabled")
        # Scroll to the end
        self.text.yview(tk.END)


class DownloaderAppGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YouTube Video Downloader")
        self.geometry("600x600")
        self.resizable(width=False, height=False)
        self.center_window(self)

        # ttk style configuration
        style = ttk.Style()
        style.theme_use("vista")

        # Logger setup
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)

        # Defining variables
        self.url_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.audio_var = tk.BooleanVar(value=True)
        self.bitrate_var = tk.StringVar()
        self.start_time_var = tk.StringVar()
        self.end_time_var = tk.StringVar()
        self.status_var = tk.DoubleVar()

        # Creating GUI
        self.create_widgets()

        # Setting up logging in GUI
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        text_handler.setFormatter(formatter)
        self.logger.addHandler(text_handler)

    def create_widgets(self):
        tk.Label(self, text="URL:").pack(pady=(10, 0))
        tk.Entry(self, textvariable=self.url_var, width=50).pack(pady=5)

        tk.Label(self, text="Save path:").pack(pady=(10, 0))
        tk.Entry(self, textvariable=self.path_var, width=50).pack(pady=5)
        tk.Button(self, text="Choose", command=self.choose_directory).pack(pady=(0, 5))

        tk.Checkbutton(self, text="Audio ON/OFF", variable=self.audio_var).pack(pady=5)
        tk.Label(self, text="Custom Bitrate (e.g., 128k):").pack(pady=(10, 0))
        tk.Entry(self, textvariable=self.bitrate_var, width=20).pack(pady=5)

        tk.Label(self, text="Custom Length - START (in seconds):").pack(pady=(10, 0))
        tk.Entry(self, textvariable=self.start_time_var, width=20).pack(pady=5)
        tk.Label(self, text="Custom Length - END (in seconds):").pack(pady=(10, 0))
        tk.Entry(self, textvariable=self.end_time_var, width=20).pack(pady=5)

        tk.Button(self, text="Download", command=self.start_download).pack(pady=20)
        self.progress_bar = ttk.Progressbar(
            self, orient="horizontal", mode="determinate", length=280
        )
        self.progress_bar.pack(pady=(20, 10))
        tk.Label(self, textvariable=self.status_var).pack()
        self.status_var.set("...")

        self.log_text = scrolledtext.ScrolledText(self, state="disabled", height=10)
        self.log_text.pack(pady=10)

        logging.info(f"{Fore.GREEN}GUI initialization successful!{Style.RESET_ALL}")

    def center_window(self, window):
        window.update_idletasks()

        width = window.winfo_width()
        height = window.winfo_height()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        x = (screen_width // 2) - (width // 2) - 20
        y = (screen_height // 2) - (height // 2) - 20

        window.geometry(f"+{x}+{y}")

        logging.info(f"{Fore.GREEN}Window successfully centered!{Style.RESET_ALL}")

    def choose_directory(self):
        directory = filedialog.askdirectory()
        self.path_var.set(directory)

    def update_status_text(self, text):
        self.status_var.set(text)
        self.update_idletasks()

    def start_progress_bar(self):
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start(10)

    def stop_progress_bar(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")

    def start_download(self):
        url = self.url_var.get()
        path = self.path_var.get()
        remove_audio = not self.audio_var.get()
        custom_bitrate = self.bitrate_var.get()
        start_time = self.start_time_var.get()
        end_time = self.end_time_var.get()

        if not url or not path:
            logging.info(
                f"{Fore.RED}Error! URL and save path are required.{Style.RESET_ALL}"
            )
            self.update_status_text("Error! URL and save path are required.")
            messagebox.showerror("Error", "URL and save path are required.")
            return

        is_path_correct = messagebox.askyesno(
            "Confirm Path", f"Is this the correct save path?\n{path}"
        )
        if not is_path_correct:
            logging.info(
                f"{Fore.YELLOW}User canceled the operation. Incorrect path.{Style.RESET_ALL}"
            )
            self.update_status_text("Operation canceled by the user. Incorrect path.")
            return

        if not os.path.exists(path) or not os.path.isdir(path):
            logging.info(
                f"{Fore.RED}Error! The specified path does not exist or is not a directory.{Style.RESET_ALL}"
            )
            self.update_status_text(
                "Error! The specified path does not exist or is not a directory."
            )
            messagebox.showerror(
                "Error", "The specified path does not exist or is not a directory."
            )
            return

        if not os.access(path, os.W_OK):
            logging.info(
                f"{Fore.RED}Error! The specified path is not writable.{Style.RESET_ALL}"
            )
            self.update_status_text("Error! The specified path is not writable.")
            messagebox.showerror("Error", "The specified path is not writable.")
            return

        # Start download in a new thread
        try:
            logging.info(f"{Fore.GREEN}Starting thread...{Style.RESET_ALL}")
            threading.Thread(
                target=self.download_video,
                args=(url, path, remove_audio, custom_bitrate, start_time, end_time),
                daemon=True,
            ).start()
        except Exception as e:
            logging.info(
                f"{Fore.RED}Error occurred while starting thread: {e}{Style.RESET_ALL}"
            )
            messagebox.showerror("Error", f"Error occurred while starting thread: {e}")

    def download_video(
        self, url, path, remove_audio, custom_bitrate, start_time, end_time
    ):
        try:
            self.after(0, self.start_progress_bar)
            temp_path = os.path.join(path, "temp")
            os.makedirs(temp_path, exist_ok=True)

            # Download video to a temporary folder
            logging.info(f"{Fore.GREEN}Downloading...{Style.RESET_ALL}")
            self.update_status_text("Downloading...")

            subprocess.run(
                ["yt-dlp", "-o", os.path.join(temp_path, "%(title)s.%(ext)s"), url],
                check=True,
            )

            downloaded_files = os.listdir(temp_path)
            if downloaded_files:
                video_path = os.path.join(temp_path, downloaded_files[0])
                need_processing = (
                    remove_audio or custom_bitrate or start_time or end_time
                )
                final_path = os.path.join(path, os.path.basename(video_path))

                if need_processing:
                    logging.info(
                        f"{Fore.LIGHTCYAN_EX}Video file requires processing!{Style.RESET_ALL}"
                    )
                    clip = VideoFileClip(video_path)

                    if remove_audio:
                        logging.info(
                            f"{Fore.LIGHTCYAN_EX}Audio will be removed during processing.{Style.RESET_ALL}"
                        )
                        clip = clip.without_audio()

                    # Trimming
                    if start_time or end_time:
                        start = float(start_time) if start_time else None
                        end = float(end_time) if end_time else None
                        clip = clip.subclip(start, end)
                        logging.info(
                            f"{Fore.LIGHTGREEN_EX}Trimming video from {start} seconds to {end} seconds...{Style.RESET_ALL}"
                        )

                    if custom_bitrate:
                        # Save the file, bitrate change happens here
                        logging.info(
                            f"{Fore.LIGHTMAGENTA_EX}Processing... Applying custom bitrate: {custom_bitrate}{Style.RESET_ALL}"
                        )
                        self.update_status_text(
                            f"Processing...\nApplying custom bitrate: {custom_bitrate}"
                        )
                        clip.write_videofile(
                            final_path,
                            bitrate=custom_bitrate,
                            ffmpeg_params=["-c:v", "h264_nvenc"],
                        )
                    else:
                        logging.info(
                            f"{Fore.LIGHTMAGENTA_EX}Processing...{Style.RESET_ALL}"
                        )
                        self.update_status_text("Processing...")
                        clip.write_videofile(
                            final_path, ffmpeg_params=["-c:v", "h264_nvenc"]
                        )

                    clip.close()
                    logging.info(f"{Fore.GREEN}Video file closed!{Style.RESET_ALL}")
                else:
                    # If no processing needed, just move the file
                    logging.info(
                        f"{Fore.LIGHTMAGENTA_EX}The file does not require reprocessing.{Style.RESET_ALL}"
                    )
                    self.update_status_text("The file does not require reprocessing.")
                    os.replace(video_path, final_path)

                self.after(0, self.stop_progress_bar)
                logging.info(f"{Fore.GREEN}Done!{Style.RESET_ALL}")
                self.update_status_text("Done!")
                messagebox.showinfo("Success", "Download and processing completed.")
            else:
                self.after(0, self.stop_progress_bar)
                logging.info(
                    f"{Fore.YELLOW}No files found to download.{Style.RESET_ALL}"
                )
                self.update_status_text("Error! No files found to download.")
                messagebox.showerror("Error", "No files found to download.")
        except Exception as e:
            self.after(0, self.stop_progress_bar)
            logging.error(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            self.update_status_text(f"Error:\n{e}")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    app = DownloaderAppGUI()
    app.mainloop()
