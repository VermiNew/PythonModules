import curses
import time
from progressbar_curses.progressbar import ProgressBar

def install_component(stdscr, progress_bar, component_name, total_steps):
    progress_bar.set_total_steps(total_steps)
    progress_bar.set_message(f"Installing {component_name}...")

    for i in range(total_steps + 1):
        progress = i / total_steps
        status_message = f"Installing {component_name} - Step {i}/{total_steps}"
        progress_bar.set_status_message(status_message)
        progress_bar.update_progress_bar(stdscr, progress)
        time.sleep(0.05)

def main(stdscr):
    curses.curs_set(0)  # Wyłącz kursor
    stdscr.clear()

    progress_bar = ProgressBar()

    # Symulacja instalacji komponentów
    components = [("Component A", 100), ("Component B", 75), ("Component C", 150), ("Component D", 25), ("Component E", 50), ("Component F", 10)]

    for component, steps in components:
        install_component(stdscr, progress_bar, component, steps)

curses.wrapper(main)
