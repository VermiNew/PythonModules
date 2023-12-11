from ball_curses.ball import AnimationModule
import curses

if __name__ == "__main__":
    # Ustawienia animacji
    num_chars = 10
    step = 5
    animation_time = 5
    screen_text = "Animation Example"
    bottom_left_text = "'CTRL + C' to quit"
    text_color_pair = 1

    # Inicjalizacja obiektu AnimationModule
    animation_module = AnimationModule(
        num_chars=num_chars,
        step=step,
        animation_time=animation_time,
        screen_text=screen_text,
        bottom_left_text=bottom_left_text,
        text_color_pair=text_color_pair
    )

    # Uruchomienie animacji
    curses.wrapper(animation_module.main)
