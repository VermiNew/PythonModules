import curses
import time

class AnimationModule:
    def __init__(self, num_chars=5, step=1, animation_time=0.5,
                 screen_text="Animation Example", bottom_left_text="'CTRL + C' to quit", text_color_pair=1):
        self.num_chars = num_chars
        self.step = step
        self.animation_time = animation_time
        self.screen_text = screen_text
        self.bottom_left_text = bottom_left_text
        self.text_color_pair = text_color_pair

    def main(self, stdscr):
        curses.curs_set(0)  # Wyłącz kursor
        stdscr.nodelay(1)   # Ustawienie trybu non-blocking dla getch()

        max_y, max_x = stdscr.getmaxyx()

        ball_speed = 1
        ball_x, ball_y = 2, max_y // 2
        direction_x = 1

        curses.start_color()
        curses.init_pair(self.text_color_pair, curses.COLOR_CYAN, curses.COLOR_BLACK)

        start_time = time.time()

        while True:
            stdscr.clear()

            # Rysuj pasek
            stdscr.addch(max_y // 2, 0, '|')
            stdscr.addch(max_y // 2, max_x - 1, '|')

            # Oblicz, czy piłka wychodzi poza ekran
            next_x = ball_x + direction_x * ball_speed * self.step
            if 1 <= next_x <= max_x - self.num_chars - 1:
                ball_x = next_x
            else:
                # Oblicz, ile miejsca jest dostępne do najbliższej krawędzi
                available_space_left = ball_x - 1
                available_space_right = max_x - self.num_chars - ball_x - 1

                # Odbicie od krawędzi, ograniczone do dostępnego miejsca
                if available_space_left < available_space_right:
                    ball_x -= available_space_left
                else:
                    ball_x += available_space_right

                # Zmiana kierunku
                direction_x *= -1

            # Rysuj piłkę jako ciąg znaków
            stdscr.addstr(ball_y, ball_x, '#' * self.num_chars)

            # Rysuj tekst na ekranie
            stdscr.addstr(0, max_x // 2 - len(self.screen_text) // 2, self.screen_text)

            # Rysuj tekst w lewym dolnym rogu
            stdscr.addstr(max_y - 1, 0, self.bottom_left_text, curses.color_pair(self.text_color_pair))

            stdscr.refresh()

            elapsed_time = time.time() - start_time
            if elapsed_time >= self.animation_time:
                break

            time.sleep(0.05)
