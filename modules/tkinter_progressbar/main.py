import threading
import time
from colorama import Fore, Style, init
from progressbar import start_progressbar

init(autoreset=True)


def update_progress(app):
    print(f"{Fore.LIGHTCYAN_EX}Progress window started!{Style.RESET_ALL}")
    max_progress = 100
    app.update_title("Title")
    for i in range(max_progress + 1):
        time.sleep(0.05)
        app.update_progress(i, f"Executing example process... {i}%")
    app.complete_progress()
    time.sleep(0.5)
    app.close_window()
    print(f"{Fore.LIGHTCYAN_EX}Progress window closed!{Style.RESET_ALL}")


if __name__ == "__main__":
    app = start_progressbar("dark")

    # Start the progress bar update in a separate thread
    threading.Thread(target=update_progress, args=(app,)).start()

    app.root.mainloop()
