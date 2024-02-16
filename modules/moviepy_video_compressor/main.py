from moviepy.editor import VideoFileClip
import os
from colorama import Style, Fore, init

init(autoreset=True)


class VideoResizer:
    def __init__(self, input_path, output_path, target_size_MB=725):
        self.input_path = input_path
        self.output_path = output_path
        self.target_size_MB = target_size_MB

    @staticmethod
    def calculate_target_bitrate(original_size, duration, target_size):
        """
        Calculates the target bitrate (in kbps) to achieve a file size smaller than target_size (MB).
        """
        target_size_bits = target_size * 8 * 1024 * 1024
        original_size_bits = original_size * 8 * 1024 * 1024
        target_bitrate = (
            target_size_bits / duration
            - (original_size_bits - target_size_bits) / duration
        )
        return max(target_bitrate, 512)  # Returns a value not less than 512 kbps

    def resize_video(self):
        """
        Reduces the video file size by attempting to lower its bitrate and optionally its resolution.
        """
        if not os.path.exists(self.input_path):
            print(f"{Fore.RED}Error: Input file does not exist.{Style.RESET_ALL}")
            return

        print(f"{Fore.YELLOW}Processing video...{Style.RESET_ALL}")
        clip = VideoFileClip(self.input_path)

        original_size = os.path.getsize(self.input_path) / (1024 * 1024)  # Size in MB
        duration = clip.duration  # Duration in seconds
        target_bitrate = self.calculate_target_bitrate(
            original_size, duration, self.target_size_MB
        )

        print(f"{Fore.GREEN}Resizing video...{Style.RESET_ALL}")
        clip.write_videofile(
            self.output_path,
            bitrate=f"{int(target_bitrate)}k",
            ffmpeg_params=["-c:v", "h264_nvenc"],
        )
        print(f"{Fore.GREEN}Video resized successfully!{Style.RESET_ALL}")


if __name__ == "__main__":
    input_video_path = input("Input file path:\n> ")
    output_video_path = input("Output file path:\n> ")
    if not os.path.exists(input_video_path):
        print(
            f"{Fore.RED}The specified input file path does not exist. Please check the path and try again.{Style.RESET_ALL}"
        )
    else:
        resizer = VideoResizer(input_video_path, output_video_path)
        resizer.resize_video()
