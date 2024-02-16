import tkinter as tk
from tkinter import ttk


class ProgressBarApp:
    def __init__(self, root):
        # Initialize the main window
        self.root = root
        self.root.title("App")
        self.root.geometry("400x100")

        # Configure the style for the progress bar
        self.style = ttk.Style(self.root)

        # Create the progress bar
        self.progress = ttk.Progressbar(
            self.root, orient="horizontal", length=300, mode="determinate"
        )
        self.progress.pack(pady=20)

        # Create a label for displaying information
        self.info_label = tk.Label(
            self.root, text="Starting...", font=("Helvetica", 10)
        )
        self.info_label.pack(pady=10)

        # Initialize progress bar values
        self.progress["value"] = 0
        self.max_value = 100
        self.progress["maximum"] = self.max_value

        # Set the default theme
        self.set_theme("light")

    def update_title(self, new_title):
        """Update the window title."""
        self.root.title(new_title)

    def set_max_value(self, max_value):
        # Set the maximum value for the progress bar
        self.max_value = max_value
        self.progress["maximum"] = self.max_value

    def update_progress(self, value, description=""):
        # Update the progress bar's value and optionally display a description
        if value > self.max_value:
            value = self.max_value
        self.progress["value"] = value
        self.info_label.config(
            text=description if description else f"Progress: {value}%"
        )
        self.root.update_idletasks()

    def complete_progress(self):
        # Convenience method to mark the progress as complete
        self.update_progress(self.max_value, "Completed!")

    def close_window(self):
        # Zamknij okno bezpiecznie z wątku, korzystając z metody after
        self.root.after(0, self.root.destroy)

    def disable_maximize_button(self):
        """Disable the maximize button."""
        self.root.resizable(0, 0)  # Prevents resizing, which also disables maximize functionality.

    def disable_close_button(self):
        """Disable the close button."""
        self.root.protocol("WM_DELETE_WINDOW", self.disable_event)

    def disable_event(self):
        """Do nothing, used to disable standard window actions."""
        pass

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()  # Ensures the window is updated
        # Gets the width and height of the window
        window_width = self.root.winfo_width() + 50
        window_height = self.root.winfo_height()
        # Calculates the center position
        position_right = int(self.root.winfo_screenwidth()/2 - window_width/2)
        position_down = int(self.root.winfo_screenheight()/2 - window_height/2)
        # Positions the window in the center of the page.
        self.root.geometry("+{}+{}".format(position_right, position_down))

    def set_theme(self, theme):
        # Change the application's theme between light and dark modes
        if theme == "dark":
            self.style.configure(
                "Horizontal.TProgressbar", background="#03C988", troughcolor="#555555"
            )
            self.root.configure(bg="#2D033B")
            self.info_label.configure(bg="#2D033B", fg="#FFFFFF")
        else:  # light theme
            self.style.configure(
                "Horizontal.TProgressbar", background="#A1EEBD", troughcolor="#CCCCCC"
            )
            self.root.configure(bg="#FFF0F5")
            self.info_label.configure(bg="#FFF0F5", fg="#000000")


def start_progressbar(theme="light"):
    # Function to initialize and start the progress bar application
    root = tk.Tk()
    app = ProgressBarApp(root)
    app.set_theme(theme)

    # Disable window features
    app.disable_maximize_button()
    app.disable_close_button()
    
    # Center the window
    app.center_window()

    return app
