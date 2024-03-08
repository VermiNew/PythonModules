from moviepy.editor import VideoFileClip
import os
from colorama import Style, Fore, init

init(autoreset=True)


class VideoResizer:
    def __init__(self, input_path, output_path, target_size_MB=None, target_bitrate=None):
        self.input_path = input_path
        self.output_path = output_path
        self.target_size_MB = target_size_MB
        self.target_bitrate = target_bitrate  # in kbps

    @staticmethod
    def calculate_target_bitrate(original_size, duration, target_size):
        target_size_bits = target_size * 8 * 1024 * 1024
        original_size_bits = original_size * 8 * 1024 * 1024
        target_bitrate = (target_size_bits / duration - (original_size_bits - target_size_bits) / duration)
        return max(target_bitrate, 512)  # Returns a value not less than 512 kbps

    def prompt_for_size_or_bitrate(self):
        choice = input("Do you want to specify the target size in MB or the target bitrate in kbps? (size/bitrate):\n> ").lower()
        if choice == 'size':
            self.target_size_MB = float(input("Enter the target size in MB:\n> "))
        elif choice == 'bitrate':
            self.target_bitrate = float(input("Enter the target bitrate in kbps:\n> "))
        else:
            print(f"{Fore.RED}Invalid choice. Please enter 'size' or 'bitrate'.{Style.RESET_ALL}")
            self.prompt_for_size_or_bitrate()

    def display_video_info(self):
        original_size = os.path.getsize(self.input_path) / (1024 * 1024)  # Size in MB
        clip = VideoFileClip(self.input_path)
        duration = clip.duration  # Duration in seconds
        print(f"Original video size: {original_size:.2f} MB")
        print(f"Video duration: {duration:.2f} seconds")

    def resize_video(self):
        if not os.path.exists(self.input_path):
            print(f"{Fore.RED}Error: Input file does not exist.{Style.RESET_ALL}")
            return

        self.display_video_info()
        self.prompt_for_size_or_bitrate()

        clip = VideoFileClip(self.input_path)
        original_size = os.path.getsize(self.input_path) / (1024 * 1024)  # Size in MB
        duration = clip.duration  # Duration in seconds

        if self.target_size_MB:
            self.target_bitrate = self.calculate_target_bitrate(original_size, duration, self.target_size_MB)

        print(f"{Fore.GREEN}Resizing video...{Style.RESET_ALL}")
        clip.write_videofile(
            self.output_path,
            bitrate=f"{int(self.target_bitrate)}k",
            ffmpeg_params=["-c:v", "h264_nvenc"],
        )
        print(f"{Fore.GREEN}Video resized successfully!{Style.RESET_ALL}")


if __name__ == "__main__":
    input_video_path = input("Input file path:\n> ")
    output_video_path = input("Output file path:\n> ")
    if not os.path.exists(input_video_path):
        print(f"{Fore.RED}The specified input file path does not exist. Please check the path and try again.{Style.RESET_ALL}")
    else:
        resizer = VideoResizer(input_video_path, output_video_path)
        resizer.resize_video()
