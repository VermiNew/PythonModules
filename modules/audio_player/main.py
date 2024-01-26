import numpy as np
import soundfile as sf
import sounddevice as sd
import math
import argparse
import sys
import shutil
import os
from scipy.signal import resample
from colorama import Fore, Style, init

init(autoreset=True)

class AudioPlayer:
    def __init__(self, file_path, max_bar_length=50, volume_scale=1.0, pitch_shift=0.0, show_info=False):
        self.file_path = file_path
        self.max_bar_length = max_bar_length
        self.volume_scale = volume_scale
        self.pitch_shift = pitch_shift
        self.show_info = show_info

    def change_volume(self, data):
        if self.show_info:
            print(f"Adjusting volume by scale factor: {self.volume_scale}")
        return data * self.volume_scale

    def change_pitch(self, data, samplerate):
        original_duration = len(data) / samplerate

        if self.pitch_shift == 0:
            if self.show_info:
                print("No pitch shift applied.")
            return data

        if self.show_info:
            print(f"Applying pitch shift: {self.pitch_shift} semitones")
        speed_factor = 2 ** (self.pitch_shift / 12)
        new_length = int(len(data) / speed_factor)

        if data.ndim == 2:  # Stereo
            new_data = np.vstack([resample(data[:,0], new_length), resample(data[:,1], new_length)]).T
        else:  # Mono
            new_data = resample(data, new_length)

        new_duration = len(new_data) / samplerate

        if self.show_info:
            print(f"Pitch shift completed.\nDuration changed from {Fore.LIGHTBLUE_EX}{original_duration:.2f}s{Style.RESET_ALL} to {Fore.LIGHTBLUE_EX}{new_duration:.2f}s{Style.RESET_ALL}")
        return np.ascontiguousarray(new_data)

    def play_audio(self):
        data, samplerate = sf.read(self.file_path, dtype='float32')
        total_samples = len(data)

        if self.show_info:
            self.display_info(data, samplerate, total_samples)

        data = self.change_volume(data)
        data = self.change_pitch(data, samplerate)

        chunk_size = 1024
        stream = sd.OutputStream(samplerate=samplerate, channels=data.shape[1])
        stream.start()

        for start in range(0, total_samples, chunk_size):
            end = start + chunk_size
            chunk = data[start:end]

            if len(chunk) == 0:
                break

            stream.write(chunk)

            self.display_volume_bar(chunk)

        stream.stop()
        stream.close()
        sys.stdout.write('\r' + ' ' * self.max_bar_length + '\r')
        sys.stdout.write(f'{Fore.CYAN}Completed! File: {Fore.LIGHTBLUE_EX}{self.file_path}{Style.RESET_ALL}\n')
        sys.stdout.flush()

    def display_info(self, data, samplerate, total_samples):
        print(f"{Fore.CYAN}Playing Audio{Style.RESET_ALL}")
        print(f"File Path: {self.file_path}")
        print(f"Sample Rate: {samplerate} Hz")
        print(f"Total Samples: {total_samples}")
        print(f"Duration: {total_samples/samplerate:.2f} seconds")
        print(f"Volume Scale: {self.volume_scale}")
        print(f"Pitch Shift: {self.pitch_shift} semitones")
        print(f"Max Bar Length: {self.max_bar_length}")
        print(f"{Fore.CYAN}Starting Playback...{Style.RESET_ALL}\n")

    def display_volume_bar(self, chunk):
        chunk_rms = np.sqrt(np.mean(chunk**2))
        bar_length = int(math.sqrt(chunk_rms) * self.max_bar_length)
        bar = '#' * bar_length
        sys.stdout.write('\r' + Fore.GREEN + bar.ljust(self.max_bar_length) + Style.RESET_ALL)
        sys.stdout.flush()

def print_help():
    help_text = f"""
    {Fore.CYAN}Audio Visualizer Help{Style.RESET_ALL}

    Usage: 
        script.py [options] file_path

    Options:
        -h, --help                      Show this help message and exit.
        -l, --length LENGTH             Set the maximum length of the volume bar.
                                        Use 'full_width' for full terminal width. Default is 50.
        -v, --volume VOLUME             Set the volume scale factor. Default is 1.0.
        -p, --pitch PITCH               Set the pitch shift in semitones. Default is 0.0.
        --ignore-volume-warning         Ignore the volume level warning.
        --no-volume-limit               Remove the maximum volume limit (use with caution).
        --show-info                     Show file and settings information before playing.

    {Fore.YELLOW}Examples:{Style.RESET_ALL}
        script.py -l full_width -v 1.0 -p 0.0 "audio.mp3"
        script.py -l 128 --no-volume-limit --ignore-volume-warning -v 15 "audio.mp3"

    {Fore.RED}Note:{Style.RESET_ALL}
        Increasing the volume beyond normal limits can cause audio distortion or damage to your speakers.
        Use the '--no-volume-limit' option with caution.
    """
    print(help_text)

def validate_file_path(file_path):
    if not os.path.exists(file_path):
        print(f"{Fore.RED}Error: The file '{file_path}' does not exist.{Style.RESET_ALL}")
        return False
    if not os.path.isfile(file_path):
        print(f"{Fore.RED}Error: '{file_path}' is not a file.{Style.RESET_ALL}")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Audio Player", add_help=False)
    parser.add_argument("file_path", nargs='?', help="Path to the audio file")
    parser.add_argument("-l", "--length", type=str, default="50", help="Max length of the volume bar or 'full_width'")
    parser.add_argument("-v", "--volume", type=float, default=1.0, help="Volume scale factor (default: 1.0)")
    parser.add_argument("-p", "--pitch", type=float, default=0.0, help="Pitch shift in semitones (default: 0.0)")
    parser.add_argument("--ignore-volume-warning", action="store_true", help="Ignore the volume level warning")
    parser.add_argument("--no-volume-limit", action="store_true", help="Remove the maximum volume limit")
    parser.add_argument("--show-info", action="store_true", help="Show file and settings information before playing")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit")

    args = parser.parse_args()

    if args.help or not args.file_path:
        print_help()
        sys.exit(0)

    if not validate_file_path(args.file_path):
        sys.exit(1)

    # Validate the length argument
    if args.length.lower() != 'full_width':
        try:
            max_bar_length = int(args.length)
            if max_bar_length <= 0:
                raise ValueError
        except ValueError:
            print(f"{Fore.RED}Error: Invalid value for '--length'. Please provide a positive integer or 'full_width'.{Style.RESET_ALL}")
            sys.exit(1)
    else:
        max_bar_length = shutil.get_terminal_size().columns

    # Validate the volume argument
    if args.volume < 0:
        print(f"{Fore.RED}Error: Volume scale factor cannot be negative.{Style.RESET_ALL}")
        sys.exit(1)

    terminal_width = shutil.get_terminal_size().columns
    max_bar_length = terminal_width if args.length.lower() == 'full_width' else min(int(args.length), terminal_width)

    max_volume_limit = 10.0
    if args.no_volume_limit:
        if not args.ignore_volume_warning:
            print(f"{Fore.YELLOW}Warning: You are exceeding the normal volume limit of {max_volume_limit}.{Style.RESET_ALL}")
            user_input = input("Do you want to proceed? (Yes/Y or No/N): ")
            if user_input.lower() not in ["yes", "y"]:
                print(f"{Fore.RED}Volume boost cancelled by user.{Style.RESET_ALL}")
                sys.exit(1)
    elif args.volume > max_volume_limit:
        print(f"{Fore.RED}Error: Volume scale factor exceeds maximum limit of {max_volume_limit}.{Style.RESET_ALL}")
        print(f"To bypass this limit, use '--no-volume-limit' (with caution).")
        sys.exit(1)

    player = AudioPlayer(args.file_path, max_bar_length, args.volume, args.pitch, args.show_info)
    player.play_audio()

if __name__ == '__main__':
    main()
