import curses
import time

class ProgressBar:
    def __init__(self):
        self.total_steps = 1
        self.message = "Progress:"
        self.status_message = ""

        self.BAR_WIDTH_PERCENTAGE = 0.8
        self.BAR_START_CHAR = '['
        self.BAR_END_CHAR = ']'
        self.BAR_FILL_CHAR = '='

    def draw_progress_bar(self, win, progress):
        max_y, max_x = win.getmaxyx()

        # Rysuj pasek postępu
        bar_width = int(max_x * self.BAR_WIDTH_PERCENTAGE)
        bar_x = int((max_x - bar_width) / 2)

        # Wyczyść obszar paska postępu
        win.addstr(max_y // 2, bar_x - 1, ' ' * (bar_width + 2))

        win.addch(max_y // 2, bar_x - 1, self.BAR_START_CHAR)
        win.addch(max_y // 2, bar_x + bar_width, self.BAR_END_CHAR)

        progress_width = int(bar_width * progress)
        for i in range(progress_width):
            win.addch(max_y // 2, bar_x + i, self.BAR_FILL_CHAR)

        # Wyczyść obszar wiadomości i statusu
        win.addstr(max_y // 2 + 2, 0, ' ' * max_x)
        win.addstr(max_y // 2 + 4, 0, ' ' * max_x)

        # Wyświetl wiadomość pod paskiem postępu
        msg_x = int((max_x - len(self.message)) / 2)
        win.addstr(max_y // 2 + 2, msg_x, self.message)

        # Wyświetl status message
        status_msg_x = int((max_x - len(self.status_message)) / 2)
        win.addstr(max_y // 2 + 4, status_msg_x, self.status_message)

        win.refresh()

    def set_status_message(self, status_message):
        self.status_message = status_message

    def set_message(self, message):
        self.message = message

    def set_total_steps(self, total_steps):
        self.total_steps = total_steps

    def update_progress_bar(self, win, progress):
        self.draw_progress_bar(win, progress)

    def run_progress_bar(self, stdscr):
        curses.curs_set(0)  # Wyłącz kursor
        stdscr.clear()

        for i in range(self.total_steps + 1):
            progress = i / self.total_steps
            self.update_progress_bar(stdscr, progress)
            time.sleep(0.1)
