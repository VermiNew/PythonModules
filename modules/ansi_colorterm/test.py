from main import ANSIColorizer as ACOLOR


def main():
    # Clear the screen
    print(ACOLOR.clear_screen())
    print("\n" * 15)

    # Simple colored text
    print(ACOLOR.style("Hello, World!", r=255, g=100, b=50, bold=True))

    # Text with background color
    print(
        ACOLOR.style("Background Color", r=255, g=255, b=255, bold=True)
        + ACOLOR.background_color(0, 100, 200)
        + " Blue Background "
        + ACOLOR.reset_background()
        + ACOLOR.reset()
    )

    # Gradient text effect
    print(
        ACOLOR.gradient_effect(
            "Color Gradient Effect", (255, 0, 0), (0, 0, 255), bold=True
        )
    )

    # Typing effect
    print("Typing Effect:")
    ACOLOR.typing_effect(
        "This is being typed out...", color=(0, 255, 0), typing_speed=0.05
    )

    # Fade out effect
    print("Fade Out Effect:")
    ACOLOR.fade_out("Fading Out...", (255, 255, 0), fade_duration=3, steps=256)

    # Fade in and out effect
    print("Fade In and Out Effect:")
    ACOLOR.fade_in_out(
        "Fading In and Out", (255, 0, 0), fade_duration=5, steps=256, delay=3
    )

    # Move cursor and print text
    print(
        ACOLOR.move_cursor(10, 10) + ACOLOR.style("Moved cursor here", r=0, g=255, b=0)
    )

    # Bold, underline, strikethrough, and italic
    print(ACOLOR.bold() + "Bold Text" + ACOLOR.reset())
    print(ACOLOR.underline() + "Underlined Text" + ACOLOR.reset())
    print(ACOLOR.strikethrough() + "Strikethrough Text" + ACOLOR.reset())
    print(ACOLOR.italic() + "Italic Text" + ACOLOR.reset())

    # Ensure all changes are reset
    print(ACOLOR.reset())


if __name__ == "__main__":
    main()
