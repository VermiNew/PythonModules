import tkinter as tk
from tkinter import messagebox
import subprocess
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def download_video(url):
    try:
        subprocess.run(['yt-dlp', url, '--output', f'mp4/%(title)s.%(ext)s'])
        messagebox.showinfo("Success", "Video downloaded successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def on_download_button_click():
    url = url_entry.get()
    if is_valid_url(url):
        download_video(url)
    else:
        messagebox.showerror("Error", "Invalid URL")

# Tworzymy główne okno
root = tk.Tk()
root.title("YouTube Video/Audio Downloader - yt-dlp")

# Dodajemy etykietę i pole tekstowe do wprowadzania URL
url_label = tk.Label(root, text="Enter YouTube URL:")
url_label.pack(pady=10)

url_entry = tk.Entry(root, width=40)
url_entry.pack(pady=10)

# Dodajemy przycisk do pobierania
download_button = tk.Button(root, text="Download", command=on_download_button_click)
download_button.pack(pady=10)

# Wyśrodkowanie okna przy starcie
window_width = 400  # szerokość okna
window_height = 200  # wysokość okna

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_coordinate = int((screen_width - window_width) / 2)
y_coordinate = int((screen_height - window_height) / 2)

root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

# Uruchamiamy pętlę zdarzeń
root.mainloop()
