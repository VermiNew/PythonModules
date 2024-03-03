import cv2
import sys
import os
import time
from colorama import Fore, Style, init
import tkinter as tk
from tkinter import ttk, messagebox
import threading

init()

# Palety
palettes = {
    "Regular": ["#", "%", "?", "+", ":", "·", "·"],
    "Inverse": ["·", "·", ":", "+", "%", "#", "#"],
    "Grayscale": ["#", "@", "O", "o", ".", ":", "+"],
    "Numbers": ["7", "6", "5", "4", "3", "2", "1", "0"],
    "Oceanic": ["~", "O", "o", "-", ".", ":", "+"]
}

# ·  ·  ·  ·  #
# Do zmiany:
# - Multithreading
# - Oczyszczenie kodu
# ·  ·  ·  ·  #

ASPECT_RATIO = 1.5  # Stosunek wysokości do szerokości czcionki

class VideoPlayer:
    def __init__(self, master):
        self.master = master
        self.master.title("ASCII Video Player Settings")
        self.video_thread = None

        self.palette_label = tk.Label(master, text="Select Palette:")
        self.palette_combobox = ttk.Combobox(master, values=list(palettes.keys()))
        self.palette_combobox.set("Regular")

        self.mode_label = tk.Label(master, text="Select Mode:")
        self.mode_combobox = ttk.Combobox(master, values=["Maintain aspect ratio", "Use max terminal space"])
        self.mode_combobox.set("Use max terminal space")

        self.file_label = tk.Label(master, text="Video File:")
        self.file_entry = tk.Entry(master)
        self.start_button = tk.Button(master, text="Start", command=self.start_video)

        self.fps_label = tk.Label(master, text="FPS (Frames per Second):")
        self.fps_entry = tk.Entry(master)
        self.fps_entry.insert(0, "60")

        self.palette_label.pack(pady=5)
        self.palette_combobox.pack(pady=5)
        self.mode_label.pack(pady=5)
        self.mode_combobox.pack(pady=5)
        self.file_label.pack(pady=5)
        self.file_entry.pack(pady=5, padx=5)
        self.fps_label.pack(pady=5)
        self.fps_entry.pack(pady=5, padx=5)
        self.start_button.pack(pady=10)

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_video(self):
        if self.video_thread and self.video_thread.is_alive():
            messagebox.showerror("Error", "Visualization is already running.")
            return

        # Pobranie danych z interfejsu
        palette_choice = self.palette_combobox.get()
        mode_choice = self.mode_combobox.get()
        file_path = self.file_entry.get()

        try:
            fps = float(self.fps_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid FPS value")
            return

        if palette_choice not in palettes:
            tk.messagebox.showerror("Error", "Invalid palette selection")
            return

        mode = 1 if mode_choice == "Maintain aspect ratio" else 2

        # Uruchomienie wątku do odtwarzania wideo
        self.video_thread = threading.Thread(target=self.play_video, args=(file_path, palette_choice, mode))
        self.video_thread.start()

    def play_video(self, file_path, palette_choice, mode):
        try:
            video = cv2.VideoCapture(file_path)
            frame_time = 1 / fps

            while True:
                success, image = video.read()
                if not success:
                    break  # Przerwanie pętli, jeśli nie ma więcej klatek

                start_time = time.time()
                self.print_frame(image, frame_time, palettes[palette_choice], mode)
                processing_time = time.time() - start_time
                sleep_time = frame_time - processing_time
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            video.release()  # Pamiętaj, aby zwolnić zasoby
            print("\x1b[0m")  # Przywrócenie domyślnych kolorów terminala
            sys.stdout.flush()

    def on_close(self):
        if self.video_thread and self.video_thread.is_alive():
            messagebox.showinfo("Info", "Please wait for the visualization to finish.")
        else:
            self.master.destroy()

    def grayscale(self, rgb):
        r, g, b = map(int, rgb)
        brightness = (r + g + b) / 3
        return brightness

    def print_frame(self, img, frame_time, palette, mode):
        current_time = time.time()

        # Znajdź rozmiary terminala
        terminal = os.get_terminal_size()
        term_width = terminal.columns
        term_height = terminal.lines

        # Zaokrąglenie szerokości do liczby parzystej dla estetyki
        if term_width % 2 != 0:
            term_width -= 1

        height, width, _ = img.shape

        # Obliczenia proporcji
        original_ratio = width / height
        width_ratio = term_width / width
        height_ratio = term_height / height

        if mode == 1:
            width_ratio = height_ratio * original_ratio * ASPECT_RATIO
            small_img = cv2.resize(img, (0, 0), fx=width_ratio, fy=height_ratio)
        elif mode == 2:
            small_img = cv2.resize(img, (0, 0), fx=width_ratio, fy=height_ratio)

        small_height, small_width, _ = small_img.shape

        # Krok przemieszczania klatki
        frame_step = small_height + 1

        # Wypełnianie pustym miejscem, jeśli trzeba
        size_difference = term_width - small_width
        if size_difference > 1:
            padding = " " * (size_difference // 2 + 1)
            small_img = cv2.putText(small_img, padding, (0, 0), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

        # Rysowanie klatki
        ascii_frame = ""
        for col in small_img:
            for row in col:
                brightness = self.grayscale(row)
                character = palette[int(brightness / 255 * (len(palette) - 1))]
                ascii_frame += f'\x1b[38;2;{row[2]};{row[1]};{row[0]}m{character}'
            ascii_frame += "\n"

        print(ascii_frame[:-1], end="")

        # Aktualizacja klatki
        while True:
            if time.time() - current_time <= frame_time:
                pass
            else:
                sys.stdout.write(f"\033[{frame_step}F")  # Przesunięcie kursora w górę o n linii
                break

# Uruchomienie interfejsu
root = tk.Tk()
app = VideoPlayer(root)
root.resizable(width=False, height=False)
root.mainloop()
