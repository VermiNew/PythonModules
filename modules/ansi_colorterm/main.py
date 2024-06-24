import shutil
import sys
import time
import logging


class ANSIColorizer:
    @staticmethod
    def color(r, g, b):
        return f"\033[38;2;{r};{g};{b}m"

    @staticmethod
    def background_color(r, g, b):
        return f"\033[48;2;{r};{g};{b}m"

    @staticmethod
    def reset():
        return "\033[0m"

    @staticmethod
    def reset_background():
        return "\033[49m"

    @staticmethod
    def bold():
        return "\033[1m"

    @staticmethod
    def underline():
        return "\033[4m"

    @staticmethod
    def strikethrough():
        return "\033[9m"

    @staticmethod
    def italic():
        return "\033[3m"

    @staticmethod
    def overline():
        return "\033[53m"

    @staticmethod
    def clear_screen():
        return "\033[2J"

    @staticmethod
    def move_cursor(x, y):
        return f"\033[{x};{y}H"

    @staticmethod
    def blink():
        return "\033[5m"

    @staticmethod
    def mix_colors(color1, color2, ratio):
        r = int(color1[0] * ratio + color2[0] * (1 - ratio))
        g = int(color1[1] * ratio + color2[1] * (1 - ratio))
        b = int(color1[2] * ratio + color2[2] * (1 - ratio))
        return r, g, b

    @classmethod
    def gradient_effect(
        cls,
        text,
        color_start,
        color_end,
        bold=False,
        underline=False,
        strikethrough=False,
    ):
        styled_text = ""
        for i, char in enumerate(text):
            ratio = i / len(text)
            r, g, b = cls.mix_colors(color_start, color_end, ratio)
            style = ""
            if bold:
                style += cls.bold()
            if underline:
                style += cls.underline()
            if strikethrough:
                style += cls.strikethrough()
            styled_text += f"{cls.color(r, g, b)}{style}{char}"
        styled_text += cls.reset()
        return styled_text

    @classmethod
    def style(
        cls,
        text,
        r=None,
        g=None,
        b=None,
        bold=False,
        underline=False,
        strikethrough=False,
    ):
        try:
            style = ""
            if r is not None and g is not None and b is not None:
                style += cls.color(r, g, b)
            if bold:
                style += cls.bold()
            if underline:
                style += cls.underline()
            if strikethrough:
                style += cls.strikethrough()
            return f"{style}{text}{cls.reset()}"
        except Exception as e:
            logging.error(f"Failed to style text: {e}", exc_info=True)
            return text

    @classmethod
    def fade_out(
        cls,
        text,
        start_color,
        fade_duration=5,
        steps=10,
        bold=False,
        underline=False,
        strikethrough=False,
    ):
        try:
            r, g, b = start_color
            for i in range(steps + 1):
                current_intensity = 255 - int((255 / steps) * i)
                faded_text = cls.style(
                    text,
                    r=min(r, current_intensity),
                    g=min(g, current_intensity),
                    b=min(b, current_intensity),
                    bold=bold,
                    underline=underline,
                    strikethrough=strikethrough,
                )
                sys.stdout.write(f"\r{faded_text}")
                sys.stdout.flush()
                time.sleep(fade_duration / steps)
            print()
        except Exception as e:
            logging.error(f"Failed to execute fade out animation: {e}", exc_info=True)

    @classmethod
    def fade_in_out(
        cls,
        text,
        color,
        fade_duration=10,
        steps=30,
        bold=False,
        underline=False,
        strikethrough=False,
        delay=0,
    ):
        try:
            r, g, b = color

            # Fade in
            for i in range(steps // 2 + 1):
                current_intensity = int((255 / (steps // 2)) * i)
                faded_text = cls.style(
                    text,
                    r=min(r, current_intensity),
                    g=min(g, current_intensity),
                    b=min(b, current_intensity),
                    bold=bold,
                    underline=underline,
                    strikethrough=strikethrough,
                )
                sys.stdout.write(f"\r{faded_text}")
                sys.stdout.flush()
                time.sleep(fade_duration / steps)

            time.sleep(delay)

            # Fade out
            for i in range(steps // 2 + 1):
                current_intensity = 255 - int((255 / (steps // 2)) * i)
                faded_text = cls.style(
                    text,
                    r=min(r, current_intensity),
                    g=min(g, current_intensity),
                    b=min(b, current_intensity),
                    bold=bold,
                    underline=underline,
                    strikethrough=strikethrough,
                )
                sys.stdout.write(f"\r{faded_text}")
                sys.stdout.flush()
                time.sleep(fade_duration / steps)
            print("")
        except Exception as e:
            logging.error(
                f"Failed to execute fade in out animation: {e}", exc_info=True
            )

    @classmethod
    def fade_in_out_center(
        cls,
        text,
        color,
        fade_duration=10,
        steps=30,
        bold=False,
        underline=False,
        strikethrough=False,
        delay=0,
        frame_step=0,
    ):
        rows = shutil.get_terminal_size().lines
        rows = int(rows / 2)
        print("\n" * rows)
        
        columns = shutil.get_terminal_size().columns
        
        # Center each line separately
        centered_lines = [line.center(columns) for line in text.split('\n')]
        centered_text = "\n".join(centered_lines)

        try:
            r, g, b = color
            # Fade in
            for i in range(steps // 2 + 1):
                current_intensity = int((255 / (steps // 2)) * i)
                faded_text = cls.style(
                    centered_text,
                    r=min(r, current_intensity),
                    g=min(g, current_intensity),
                    b=min(b, current_intensity),
                    bold=bold,
                    underline=underline,
                    strikethrough=strikethrough,
                )
                sys.stdout.write(faded_text)
                sys.stdout.write(f"\033[{frame_step}F")
                sys.stdout.flush()
                time.sleep(fade_duration / steps)

            time.sleep(delay)

            # Fade out
            for i in range(steps // 2 + 1):
                current_intensity = 255 - int((255 / (steps // 2)) * i)
                faded_text = cls.style(
                    centered_text,
                    r=min(r, current_intensity),
                    g=min(g, current_intensity),
                    b=min(b, current_intensity),
                    bold=bold,
                    underline=underline,
                    strikethrough=strikethrough,
                )
                sys.stdout.write(faded_text)
                sys.stdout.write(f"\033[{frame_step}F")
                sys.stdout.flush()
                time.sleep(fade_duration / steps)
            print("")
        except Exception as e:
            logging.error(
                f"Failed to execute fade in out animation: {e}", exc_info=True
            )

    @classmethod
    def typing_effect(
        cls,
        text,
        color=None,
        typing_speed=0.1,
        bold=False,
        underline=False,
        strikethrough=False,
    ):
        r, g, b = color if color else (255, 255, 255)
        try:
            for char in text:
                styled_char = cls.style(
                    char,
                    r,
                    g,
                    b,
                    bold=bold,
                    underline=underline,
                    strikethrough=strikethrough,
                )
                sys.stdout.write(styled_char)
                sys.stdout.flush()
                time.sleep(typing_speed)
            print()
        except Exception as e:
            logging.error(f"Failed to execute typing effect: {e}", exc_info=True)
