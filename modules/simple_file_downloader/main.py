import argparse
import requests
from tqdm import tqdm
from hashlib import sha256
from colorama import Fore, Style, init
import os
import sys

init(autoreset=True)

class SimpleFileDownloader:
    def __init__(self, url, filename):
        self.url = url
        self.filename = filename
        self.tmp_filename = filename + ".tmp"

    def download_file(self, filename):
        try:
            response = requests.get(self.url, stream=True)
            total_size_in_bytes = int(response.headers.get('content-length', 0))
            block_size = 1024
            progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
            with open(filename, 'wb') as file:
                for data in response.iter_content(block_size):
                    progress_bar.update(len(data))
                    file.write(data)
            progress_bar.close()
            if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                print(f"{Fore.RED}ERROR: Something went wrong during the download{Style.RESET_ALL}")
                return False
            return True
        except Exception as e:
            print(f"{Fore.RED}An error occurred during the download: {e}{Style.RESET_ALL}")
            return False

    def verify_file(self, filename):
        sha256_hash = sha256()
        with open(filename,"rb") as file:
            for byte_block in iter(lambda: file.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def run(self):
        print(f"{Fore.BLUE}Starting download...{Style.RESET_ALL}")
        if self.download_file(self.filename):
            print(f"{Fore.GREEN}Download completed successfully.{Style.RESET_ALL}")

            print(f"{Fore.BLUE}Verifying file...{Style.RESET_ALL}")
            first_checksum = self.verify_file(self.filename)
            print(f"{Fore.CYAN}First checksum: {first_checksum}{Style.RESET_ALL}")

            print(f"{Fore.BLUE}Downloading the file again for secondary verification...{Style.RESET_ALL}")
            if self.download_file(self.tmp_filename):
                print(f"{Fore.GREEN}Second download completed successfully.{Style.RESET_ALL}")

                print(f"{Fore.BLUE}Verifying file again...{Style.RESET_ALL}")
                second_checksum = self.verify_file(self.tmp_filename)
                print(f"{Fore.CYAN}Second checksum: {second_checksum}{Style.RESET_ALL}")
                os.remove(self.tmp_filename)

                if first_checksum == second_checksum:
                    print(f"{Fore.GREEN}File verification successful!{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}File verification failed. The two downloads do not match.{Style.RESET_ALL}")

    @staticmethod
    def show_help():
        help_text = f"""
{Fore.LIGHTMAGENTA_EX}Simple File Downloader{Style.RESET_ALL}

{Fore.CYAN}Usage:{Style.RESET_ALL}
  script.py [options]

{Fore.CYAN}Options:{Style.RESET_ALL}
{Fore.GREEN}--url{Style.RESET_ALL}         URL of the file to download. {Fore.RED}(required){Style.RESET_ALL}
{Fore.GREEN}--output{Style.RESET_ALL}      Filename to save the downloaded file as. {Fore.RED}(required){Style.RESET_ALL}
{Fore.GREEN}--help{Style.RESET_ALL}        Show this help message and exit{Style.RESET_ALL}

{Fore.CYAN}Examples:{Style.RESET_ALL}
{Fore.GREEN}main.py{Style.RESET_ALL} {Fore.LIGHTBLUE_EX}--url{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}<file_url>{Style.RESET_ALL} {Fore.LIGHTBLUE_EX}--output{Style.RESET_ALL} {Fore.LIGHTMAGENTA_EX}<output_filename>{Style.RESET_ALL}
{Fore.GREEN}main.py{Style.RESET_ALL} {Fore.LIGHTBLUE_EX}--help{Style.RESET_ALL}"""
        print(help_text)
        sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and verify a file from a URL.", add_help=False)
    parser.add_argument("--url", help="URL of the file to download")
    parser.add_argument("--output", help="Filename to save the downloaded file as")
    parser.add_argument("--help", action="store_true", help="Show this help message and exit")

    args, unknown = parser.parse_known_args()

    if args.help or unknown or args.url is None or args.output is None:
        SimpleFileDownloader.show_help()
        sys.exit()

    downloader = SimpleFileDownloader(args.url, args.output)
    downloader.run()
