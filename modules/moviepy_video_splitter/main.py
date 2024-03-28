import os
import math
import argparse
import logging
import shutil
from moviepy.editor import VideoFileClip
from colorama import Fore, Style, init
from rich.traceback import install

# Setup for handling exceptions with rich for better readability
install()

# Initialize Colorama for colored terminal output
init(autoreset=True)

# Configure logging for informational messages and error handling
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


class VideoSplitter:
    def __init__(self, input_file):
        self.input_file = self.validate_path(input_file)

    def calculate_bitrate(self):
        try:
            clip = VideoFileClip(self.input_file)
            file_size_bytes = os.path.getsize(self.input_file)
            duration_seconds = clip.duration
            # Bitrate in kbps
            bitrate = int((file_size_bytes * 8) / duration_seconds / 1000)
            return bitrate
        except Exception as e:
            logger.error(f"Error calculating bitrate: {e}")
            return None

    def split_by_size(self, max_size_mb):
        try:
            clip = VideoFileClip(self.input_file)
            duration = clip.duration
            total_size_bytes = os.path.getsize(self.input_file)
            total_size_mb = total_size_bytes / (1024 * 1024)

            if total_size_mb <= max_size_mb:
                print(
                    f"{Fore.YELLOW}File is already less than {max_size_mb}MB{Style.RESET_ALL}"
                )
                return

            # Calculate the duration for each segment based on size
            part_duration = (max_size_mb / total_size_mb) * duration
            bitrate = self.calculate_bitrate()
            return self.split_video(part_duration, bitrate)
        except Exception as e:
            logger.error(f"Error during splitting by size: {e}")

    def split_by_time(self, segment_length_sec):
        try:
            return self.split_video(segment_length_sec)
        except Exception as e:
            logger.error(f"Error during splitting by time: {e}")

    def split_video(self, segment_duration, bitrate=None):
        clip = VideoFileClip(self.input_file)
        duration = clip.duration
        parts = math.ceil(duration / segment_duration)
        output_files = []

        input_dir = os.path.dirname(self.input_file)
        base_filename = os.path.basename(self.input_file)
        filename_without_ext = os.path.splitext(base_filename)[0]
        output_dir_name = f"splitted_{filename_without_ext}"
        output_dir_path = os.path.join(input_dir, output_dir_name)

        if not os.path.exists(output_dir_path):
            os.makedirs(output_dir_path)

        for part in range(parts):
            start_time = part * segment_duration
            end_time = min((part + 1) * segment_duration, duration)

            new_clip = clip.subclip(start_time, end_time)
            new_clip_name = os.path.join(
                output_dir_path, f"{filename_without_ext}_part{part+1}.mp4"
            )
            ffmpeg_params = ["-c:v", "h264_nvenc"]

            if bitrate:
                ffmpeg_params.extend(["-b:v", f"{bitrate}k"])
                print(
                    f"{Fore.LIGHTBLUE_EX}Setting bitrate... {Fore.LIGHTCYAN_EX}{bitrate}k{Style.RESET_ALL}"
                )
            print(
                f"{Fore.LIGHTBLUE_EX}Parameters: {Fore.LIGHTCYAN_EX}{ffmpeg_params}{Style.RESET_ALL}"
            )

            new_clip.write_videofile(
                new_clip_name,
                codec="libx264",
                audio_codec="aac",
                ffmpeg_params=ffmpeg_params,
            )

            print_line_terminal_width("-")
            print(
                f'{Fore.GREEN}Created: {Fore.LIGHTYELLOW_EX}"{new_clip_name}"{Style.RESET_ALL}'
            )
            print_line_terminal_width("-")

            output_files.append(new_clip_name)

        return output_files

    @staticmethod
    def file_info(input_file):
        if not os.path.exists(input_file):
            print(f"{Fore.RED}File does not exist: {input_file}{Style.RESET_ALL}")
            exit(1)
        try:
            clip = VideoFileClip(input_file)
            print(f"{Fore.CYAN}File:{Style.RESET_ALL} {input_file}")
            print(f"{Fore.CYAN}Duration:{Style.RESET_ALL} {clip.duration}s")
            print(
                f"{Fore.CYAN}Size:{Style.RESET_ALL} {os.path.getsize(input_file) / (1024*1024):.2f}MB"
            )
        except Exception as e:
            logger.error(f"Error reading file information: {e}")
            exit(1)

    @staticmethod
    def validate_path(input_file):
        if not os.path.isfile(input_file):
            logger.error(f"Invalid file path: {input_file}")
            exit(1)
        return input_file


def print_line_terminal_width(char="-"):
    width = shutil.get_terminal_size().columns
    print(char * width)


def main():
    parser = argparse.ArgumentParser(
        description="Split an MP4 video file into smaller chunks."
    )
    parser.add_argument(
        "-i", "--input_file", type=str, required=True, help="Path to the input MP4 file"
    )
    parser.add_argument("-bs", "--by-size", type=float, help="Split by size (in MB)")
    parser.add_argument("-bt", "--by-time", type=int, help="Split by time (in seconds)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if not (args.by_size or args.by_time):
        print(
            f"{Fore.RED}You must specify either --by-size or --by-time.{Style.RESET_ALL}"
        )
        exit(1)

    VideoSplitter.file_info(args.input_file)

    splitter = VideoSplitter(args.input_file)
    if args.by_size:
        output_files = splitter.split_by_size(args.by_size)
    elif args.by_time:
        output_files = splitter.split_by_time(args.by_time)

    if output_files:
        print("\n")
        print_line_terminal_width("-")
        print(f"{Fore.LIGHTCYAN_EX}Exported files:{Style.RESET_ALL}")
        for file in output_files:
            print(f"{Fore.CYAN}{file}{Style.RESET_ALL}")
        print_line_terminal_width("-")


if __name__ == "__main__":
    main()
