from moviepy.editor import VideoFileClip
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
from colorama import init, deinit, Fore, Style

# Initialize Colorama
init(autoreset=True)

def convert_video_to_audio(input_path, output_path, audio_codec='mp3'):
    try:
        video = VideoFileClip(input_path)
        video.audio.write_audiofile(output_path, codec=audio_codec)
        video.close()
    except Exception as e:
        print(Fore.RED + f"Error converting {input_path}: {e}" + Style.RESET_ALL)

def convert_mp4_to_wav(input_file, output_file):
    try:
        video_clip = VideoFileClip(input_file)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_file, codec='pcm_s16le')
        audio_clip.close()
        video_clip.close()
    except Exception as e:
        print(Fore.RED + f"Error converting {input_file}: {e}" + Style.RESET_ALL)

def convert_mp4_to_ogg(input_file, output_file):
    try:
        video_clip = VideoFileClip(input_file)
        audio_clip = video_clip.audio
        audio_clip.write_audiofile(output_file, codec='libvorbis')
        audio_clip.close()
        video_clip.close()
    except Exception as e:
        print(Fore.RED + f"Error converting {input_file}: {e}" + Style.RESET_ALL)

def batch_convert_videos(input_folder, output_folder, audio_format='mp3', progress_var=None):
    if not os.path.exists(input_folder):
        print(Fore.RED + f"Input folder {input_folder} does not exist." + Style.RESET_ALL)
        return

    if not os.path.exists(output_folder):
        print(Fore.YELLOW + f"Output folder {output_folder} does not exist. Creating folder..." + Style.RESET_ALL)
        os.makedirs(output_folder)

    video_files = [filename for filename in os.listdir(input_folder) if filename.endswith(".mp4")]
    total_files = len(video_files)

    for i, filename in enumerate(video_files, start=1):
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + f".{audio_format}"
        output_path = os.path.join(output_folder, output_filename)

        print(f"{Fore.GREEN}Converting {filename} to {output_filename}... ({i}/{total_files}){Style.RESET_ALL}")

        try:
            if audio_format == 'wav':
                convert_mp4_to_wav(input_path, output_path)
            elif audio_format == 'ogg':
                convert_mp4_to_ogg(input_path, output_path)
            else:
                convert_video_to_audio(input_path, output_path, audio_codec=audio_format)
        except Exception as e:
            print(Fore.RED + f"Error converting {filename}: {e}" + Style.RESET_ALL)

        # Update progress bar
        if progress_var:
            progress_value = int((i / total_files) * 100)
            progress_var.set(progress_value)

    print(Fore.GREEN + "Conversion completed!" + Style.RESET_ALL)
    progress_label.config(text="")

def convert_button_clicked():
    input_folder_path = input_folder_var.get()
    output_folder_path = output_folder_var.get()
    selected_format = format_combobox.get()

    if not input_folder_path or not output_folder_path:
        messagebox.showerror("Error", "Please select input and output folders.")
        return

    progress_var.set(0)  # Reset progress bar
    progress_label.config(text="Converting...")

    # Run conversion in a separate thread to prevent UI freeze
    conversion_thread = Thread(target=batch_convert_videos, args=(input_folder_path, output_folder_path, selected_format, progress_var))
    conversion_thread.start()

def browse_input_folder():
    input_folder_var.set(filedialog.askdirectory())

def browse_output_folder():
    output_folder_var.set(filedialog.askdirectory())

def on_close():
    print("\nClosing the program.")
    deinit()  # Cleanup Colorama resources
    root.destroy()

# Create the main Tkinter window
root = tk.Tk()
root.title("Video to Audio Converter")

# Input Folder
tk.Label(root, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5)
input_folder_var = tk.StringVar()
input_folder_entry = tk.Entry(root, textvariable=input_folder_var)
input_folder_entry.grid(row=0, column=1, padx=10, pady=5)
input_folder_button = tk.Button(root, text="Browse", command=browse_input_folder)
input_folder_button.grid(row=0, column=2, padx=10, pady=5)

# Output Folder
tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=5)
output_folder_var = tk.StringVar()
output_folder_entry = tk.Entry(root, textvariable=output_folder_var)
output_folder_entry.grid(row=1, column=1, padx=10, pady=5)
output_folder_button = tk.Button(root, text="Browse", command=browse_output_folder)
output_folder_button.grid(row=1, column=2, padx=10, pady=5)

# Output Format ComboBox
tk.Label(root, text="Output Format:").grid(row=2, column=0, padx=10, pady=5)
formats = ['mp3', 'wav', 'ogg']
format_combobox = ttk.Combobox(root, values=formats, state="readonly")
format_combobox.set(formats[0])
format_combobox.grid(row=2, column=1, padx=10, pady=5)

# Convert Button
convert_button = tk.Button(root, text="Convert", command=convert_button_clicked)
convert_button.grid(row=3, column=0, columnspan=3, pady=10)

# Progress Bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, length=300, mode='determinate')
progress_bar.grid(row=4, column=0, columnspan=3, pady=5)

# Progress Label
progress_label = tk.Label(root, text="")
progress_label.grid(row=5, column=0, columnspan=3, pady=5)

# Bind the close event to the on_close function
root.protocol("WM_DELETE_WINDOW", on_close)

# Set the window to be non-resizable
root.resizable(width=False, height=False)

# Start the Tkinter event loop
root.mainloop()
