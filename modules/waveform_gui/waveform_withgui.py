import pygame
import pyaudio
import wave
import struct
import os
import time
import tkinter as tk

# Get the current path
current_path = os.path.dirname(os.path.abspath(__file__))

# Display the path
print(f"Script path: {current_path}")
time.sleep(1)

os.system("cls & title Waveform - Python")

# Constants
SIZE = (800, 600)
BGCOLOR = (0, 0, 0)
LINECOLOR = (0, 255, 255)
READ_LENGTH = 512
Y_SCALE = float(input("Enter the amplification of the Y-axis (Real number, e.g., 2.5): "))
VOLUME_BAR_LENGTH = 50

# Sound Meter Constants
SOUND_METER_X = 20
SOUND_METER_Y = 20
SOUND_METER_WIDTH = 20
SOUND_METER_HEIGHT = 150
SOUND_METER_MAX_LEVEL = 32767

# Tkinter Constants
TK_SIZE = (400, 180)

# Initialize Pygame
pygame.init()
pygame.display.set_caption('Podgląd fali dźwiękowej')
pygame.mouse.set_visible(0)
screen = pygame.display.set_mode(SIZE)

# Load the music file
wf = wave.open(current_path + "/" + input("Enter the path to the WAV file: "), 'rb')

# Create PyAudio object
p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    print(i, p.get_device_info_by_index(i)['name'])
index = input("Enter the device index: ")

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output_device_index=int(index),
                output=True)

# Tkinter Setup
root = tk.Tk()
root.title("Waveform Player")
root.geometry(f"{TK_SIZE[0]}x{TK_SIZE[1]}")

# Tkinter Variables
current_time = tk.DoubleVar()
total_time = tk.DoubleVar()
volume_value = tk.DoubleVar(value=1.0)  # Default volume is set to 1.0

# Tkinter Callbacks
def on_scale_change(value):
    new_time = float(value)
    stream.stop_stream()
    wf.setpos(int(new_time * wf.getframerate()))
    stream.start_stream()

def update_timer_display():
    timer_label.config(text=f"Time: {int(current_time.get())}s / {int(total_time.get())}s")
    root.after(1000, update_timer_display)  # Update every second

def update_volume(value):
    volume = float(value)
    volume_label.config(text=f"Volume: {volume:.2%}")

# Tkinter Widgets
scale = tk.Scale(root, from_=0, to=wf.getnframes() / wf.getframerate(), orient="horizontal",
                 variable=current_time, length=TK_SIZE[0] - 20, showvalue=False, command=on_scale_change)
scale.pack(pady=20)

# New widgets for timer and volume control
timer_label = tk.Label(root, text="Time: 0s / 0s")
timer_label.pack()

volume_scale = tk.Scale(root, from_=0.0, to=1.0, orient="horizontal",
                        variable=volume_value, length=TK_SIZE[0] - 20, resolution=0.01, label="Volume",
                        command=lambda value: update_volume(value), sliderrelief='flat', sliderlength=15)
volume_scale.pack()

volume_label = tk.Label(root, text="Volume: 100.00%")
volume_label.pack()

# Create a surface to draw the waveform
surface = pygame.Surface((SIZE[0], SIZE[1]))

# Start the game loop
running = True
prev_y = SIZE[1] // 2
update_timer_display()  # Start the timer display function
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read the next frames from the music file
    input_time = time.time()
    time.sleep(0.00025)
    frames = wf.readframes(READ_LENGTH)
    input_time = int((time.time() - input_time) * 1000)  # czas odpowiedzi w ms

    # If there are no more frames, stop the game loop
    if not frames:
        running = False

    # Convert the frames to integers
    data = struct.unpack(f"{READ_LENGTH * wf.getnchannels()}h", frames)

    # Clear the surface
    surface.fill(BGCOLOR)

    # Draw the waveform
    for i in range(0, len(data), 2):
        x = int(i / 2 / READ_LENGTH * SIZE[0])
        y = int((data[i] / 32767) * SIZE[1] / 2 * Y_SCALE) + SIZE[1] // 2
        pygame.draw.line(surface, LINECOLOR, (x-1, prev_y), (x, y))
        prev_y = y

    # Calculate volume level
    volume = max(abs(max(data)), abs(min(data))) / SOUND_METER_MAX_LEVEL

    # Display volume bar in console
    volume_bar = int(VOLUME_BAR_LENGTH * volume)
    print("Debug: ", y, prev_y, end="  ")
    print("Volume: [{}{}] {:.2%} {}".format("#" * volume_bar, " " * (VOLUME_BAR_LENGTH - volume_bar), volume, f"{input_time} ms"), end="  \r")

    # Draw sound meter
    pygame.draw.rect(surface, (0, 255, 0), (SOUND_METER_X, SOUND_METER_Y + SOUND_METER_HEIGHT, SOUND_METER_WIDTH, 0))
    meter_height = int(volume * SOUND_METER_HEIGHT)
    pygame.draw.rect(surface, (255, 0, 0) if volume > 0.8 else (255, 165, 0) if volume > 0.6 else (255, 255, 0) if volume > 0.4 else (0, 255, 0), (SOUND_METER_X, SOUND_METER_Y + SOUND_METER_HEIGHT - meter_height, SOUND_METER_WIDTH, meter_height))

    # Update Tkinter scale
    current_time.set(wf.tell() / wf.getframerate())
    total_time.set(wf.getnframes() / wf.getframerate())

    # Update volume control display
    volume_label.config(text=f"Volume: {volume_value.get():.2%}")

    # Scale the audio data based on the volume
    scaled_frames = struct.pack(f"{READ_LENGTH * wf.getnchannels()}h", *[int(frame * volume_value.get()) for frame in data])

    # Write the frames to the audio stream
    stream.write(scaled_frames)

    # Blit the surface to the screen
    screen.blit(surface, surface.get_rect())

    # Update the display
    pygame.display.flip()

    # Update Tkinter
    root.update()

# Stop and close the audio stream
stream.stop_stream()
stream.close()

# Terminate PyAudio
p.terminate()

# Quit Pygame
pygame.quit()

# Close Tkinter window
root.destroy()
