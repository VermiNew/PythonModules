import argparse
import hashlib
import os
import requests
import ctypes
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

class FileDownloader:
    def __init__(self, urls, file_names, output_dir, show_info, show_header_info, double_check, ignore_download_check, no_beep):
        self.urls = urls
        self.file_names = file_names
        self.output_dir = output_dir
        self.show_info = show_info
        self.show_header_info = show_header_info
        self.double_check = double_check
        self.ignore_download_check = ignore_download_check
        self.no_beep = no_beep

    def download_files(self):
        for i, url in enumerate(self.urls):
            file_name = self.file_names[i] if i < len(self.file_names) else os.path.basename(url)
            save_path = os.path.join(self.output_dir, file_name)
            self.download_file(url, save_path)
        self.play_system_sound()

    def download_file(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            if self.show_header_info:
                print(f"{Fore.YELLOW}Header Information: {response.headers}{Style.RESET_ALL}")

            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 1024
            with open(save_path, "wb") as file, tqdm(
                desc=f"{Fore.CYAN}Downloading{Style.RESET_ALL}", 
                total=total_size, 
                unit='iB', 
                unit_scale=True, 
                unit_divisor=chunk_size, 
            ) as bar:
                for data in response.iter_content(chunk_size=chunk_size):
                    size = file.write(data)
                    bar.update(size)

            if self.double_check:
                self.perform_double_check(url, save_path)

            if self.show_info:
                print(f"{Fore.GREEN}Downloaded {url} to {save_path}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Error downloading {url}: {e}{Style.RESET_ALL}")

    def perform_double_check(self, url, save_path):
        temp_save_path = save_path + ".tmp"
        first_hash = self.hash_file(save_path)
        self.download_file(url, temp_save_path)
        second_hash = self.hash_file(temp_save_path)
        if first_hash == second_hash:
            os.rename(temp_save_path, save_path)
            print(f"{Fore.GREEN}File downloaded and verified successfully.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}File integrity check failed. The two downloads do not match.{Style.RESET_ALL}")
            os.remove(temp_save_path)

    @staticmethod
    def hash_file(file_path):
        BUF_SIZE = 65536  
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)
        return sha1.hexdigest()

    def play_system_sound(self):
        if not self.no_beep:
            ctypes.windll.user32.MessageBeep(0xFFFFFFFF)

    @staticmethod
    def print_help():
        help_text = f"""
{Fore.CYAN}File Downloader Help{Style.RESET_ALL}

Usage: 
    script.py --urls "url1" "url2" --file_names "name1" "name2" [options]

Options:
    -h, --help                          Show this help message and exit.
    -u, --urls URLS                     List of URLs to download. Each URL should be in quotes.
    -fn, --file_names FILE_NAMES        List of file names for the downloaded files. Each name should be in quotes.
    -o, --output OUTPUT                 Set the output directory. Default is the current directory.
    -s, --show-info                     Show information during the download.
    -shi, --show-header-info            Show HTTP header information.
    -d, --double-check                  Perform a double download for file integrity check.
    -i, --ignore-download-check         Ignore the preliminary download check.
    -n, --no-beep                       Disable the beep sound after download completion.
    --gui                               Use GUI mode for input.

{Fore.YELLOW}Examples:{Style.RESET_ALL}
    script.py --urls "http://example.com/file1.zip" "http://example.com/file2.zip" --file_names "file1.zip" "file2.zip"
    script.py --output "C:\\Users\\Your_Name\\Downloads" --show-info --urls "http://example.com/file1.zip"
    script.py --gui
    script.py --no-beep --urls "http://example.com/file1.zip"

{Fore.RED}Note:{Style.RESET_ALL}
    Ensure URLs are quoted if they contain special characters.
    The --gui option allows for interactive input but ignores other command line arguments.
    The --no-beep option is useful in environments where a beep sound is not desired.
"""
        print(help_text)

def main():
    parser = argparse.ArgumentParser(description="File Downloader Script", add_help=False)
    parser.add_argument("-u", "--urls", nargs="+", help="URLs of the files to download")
    parser.add_argument("-fn", "--file_names", nargs="+", help="Names of the files to save")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    parser.add_argument("-s", "--show-info", action="store_true", help="Show download information")
    parser.add_argument("-shi", "--show-header-info", action="store_true", help="Show header information")
    parser.add_argument("-d", "--double-check", action="store_true", help="Perform double check of downloaded file")
    parser.add_argument("-i", "--ignore-download-check", action="store_true", help="Ignore download check")
    parser.add_argument("-n", "--no-beep", action="store_true", help="No beep sound after download completion")
    parser.add_argument("--gui", action="store_true", help="Use GUI mode for input")
    parser.add_argument("-h", "--help", action="store_true", help="Show help message and exit")
    args = parser.parse_args()

    if args.gui:
        args.urls = []
        args.file_names = []
        while True:
            url = input(f"{Fore.LIGHTBLUE_EX}Enter the URL (or type 'done' to finish):{Style.RESET_ALL}\n> ")
            if url.lower() == 'done':
                break
            args.urls.append(url)
            file_name = input(f"{Fore.LIGHTBLUE_EX}Enter the file name for this URL (or press Enter to use default):{Style.RESET_ALL}\n> ")
            if file_name:
                args.file_names.append(file_name)

        args.output = input(f"{Fore.LIGHTBLUE_EX}Enter the output directory (or press Enter to use current):{Style.RESET_ALL}\n> ") or "."

    if args.help or not args.urls:
        FileDownloader.print_help()
        return

    downloader = FileDownloader(
        urls=args.urls,
        file_names=args.file_names,
        output_dir=args.output,
        show_info=args.show_info,
        show_header_info=args.show_header_info,
        double_check=args.double_check,
        ignore_download_check=args.ignore_download_check,
        no_beep=args.no_beep
    )
    downloader.download_files()

if __name__ == "__main__":
    main()
