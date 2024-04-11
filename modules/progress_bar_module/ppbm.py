import shutil
import time
from datetime import timedelta
from colorama import Fore, Style, init, deinit

# Initialize colorama
init(autoreset=True)


class ProgressBar:
    def __init__(
        self,
        total,
        bar_length=0,
        task="Progress",
        color=Fore.GREEN,
        description_color=Fore.WHITE,
        percent_color=Fore.WHITE,
        custom_text="",
    ):
        """
        Initializes the progress bar.

        Attributes:
            total (int): The total number of steps in the progress.
            bar_length (int): The length of the progress bar. If 0, it adjusts to the terminal width. Default is 0.
            task (str): The description of the task being performed. It may be truncated to fit the terminal width.
            color (colorama.Fore): The color of the progress bar itself. Default is Fore.GREEN.
            description_color (colorama.Fore): The color of the task description. Default is Fore.WHITE.
            percent_color (colorama.Fore): The color of the percentage display. Default is Fore.WHITE.
            custom_text (str): Additional text to display after the percentage. Default is an empty string.
        """
        if total <= 0:
            print(
                f"{Fore.RED}Error: The 'total' value must be greater than 0.{Style.RESET_ALL}"
            )
            raise ValueError("The 'total' value must be greater than 0.")

        self.total = total
        self.bar_length = bar_length
        self.task = self._truncate_task(task)
        self.color = color
        self.description_color = description_color
        self.percent_color = percent_color
        self.custom_text = custom_text
        self.start_time = time.time()
        self.iteration = 0
        self.is_complete = False

    def _truncate_task(self, task):
        """Shortens the task text if it exceeds 50% of the console width."""
        try:
            terminal_width = shutil.get_terminal_size().columns
            max_length = terminal_width // 2
            if len(task) > max_length:
                return task[: max_length - 3] + "..."
            return task
        except Exception as e:
            print(f"{Fore.RED}Error while truncating task text: {e}{Style.RESET_ALL}")
            raise

    def update(self, iteration=None, custom_text=None):
        """
        Updates the progress bar to a specified iteration step and optionally updates the custom text.
        """
        try:
            if custom_text is not None:
                self.custom_text = custom_text

            if self.is_complete:
                return

            if iteration is not None:
                self.iteration = iteration
            else:
                self.iteration += 1

            self._display()

            if self.iteration >= self.total:
                self._complete()
        except Exception as e:
            print(
                f"{Fore.RED}Error while updating the progress bar: {e}{Style.RESET_ALL}"
            )
            raise

    def _display(self):
        """Displays the progress bar."""
        try:
            elapsed_time = time.time() - self.start_time
            estimated_total_time = (
                elapsed_time / self.iteration * self.total if self.iteration > 0 else 0
            )
            remaining_time = max(0, estimated_total_time - elapsed_time)

            elapsed_str = str(timedelta(seconds=int(elapsed_time)))
            remaining_str = str(timedelta(seconds=int(remaining_time)))

            terminal_width = shutil.get_terminal_size().columns
            available_space = (
                terminal_width
                - len(self.task)
                - len(elapsed_str)
                - len(remaining_str)
                - len(self.custom_text)
                - 14
            )

            if self.bar_length <= 0 or self.bar_length > available_space:
                self.bar_length = available_space

            percent = f"{int((self.iteration / self.total) * 100)}%"
            filled_length = int(round(self.iteration / self.total * self.bar_length))
            arrow = "-" * (filled_length - 1) + ">" if filled_length > 0 else ""
            spaces = " " * (self.bar_length - len(arrow))

            print(
                f"{self.description_color}{self.task}: {self.color}[{arrow}{spaces}]{Style.RESET_ALL} {self.percent_color}{percent} {elapsed_str} / {remaining_str} {self.custom_text}{Style.RESET_ALL}",
                end="\r",
            )
        except Exception as e:
            print(
                f"{Fore.RED}Error while displaying the progress bar: {e}{Style.RESET_ALL}"
            )
            raise

    def _complete(self):
        """
        Finalizes the progress bar operation and deinitializes Colorama.
        """
        self.is_complete = True
        print()
        try:
            deinit()
        except Exception as e:
            print(f"Error deinitializing Colorama: {e}")
