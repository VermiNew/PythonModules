from main import ANSIColorizer


def main():
    # Clear the screen
    print(ANSIColorizer.clear_screen())
    print("\n" * 15)

    # Simple colored text
    print(ANSIColorizer.style("Hello, World!", r=255, g=100, b=50, bold=True))

    # Text with background color
    print(
        ANSIColorizer.style("Background Color", r=255, g=255, b=255, bold=True)
        + ANSIColorizer.background_color(0, 100, 200)
        + " Blue Background "
        + ANSIColorizer.reset_background()
        + ANSIColorizer.reset()
    )

    # Gradient text effect
    print(
        ANSIColorizer.gradient_effect(
            "Color Gradient Effect", (255, 0, 0), (0, 0, 255), bold=True
        )
    )

    # Typing effect
    print("Typing Effect:")
    ANSIColorizer.typing_effect(
        "This is being typed out...", color=(0, 255, 0), typing_speed=0.05
    )

    # Fade out effect
    print("Fade Out Effect:")
    ANSIColorizer.fade_out("Fading Out...", (255, 255, 0), fade_duration=3, steps=256)

    # Fade in and out effect
    print("Fade In and Out Effect:")
    ANSIColorizer.fade_in_out(
        "Fading In and Out", (255, 0, 0), fade_duration=5, steps=256, delay=3
    )

    # Move cursor and print text
    print(
        ANSIColorizer.move_cursor(10, 10) + ANSIColorizer.style("Moved cursor here", r=0, g=255, b=0)
    )

    # Bold, underline, strikethrough, and italic
    print(ANSIColorizer.bold() + "Bold Text" + ANSIColorizer.reset())
    print(ANSIColorizer.underline() + "Underlined Text" + ANSIColorizer.reset())
    print(ANSIColorizer.strikethrough() + "Strikethrough Text" + ANSIColorizer.reset())
    print(ANSIColorizer.italic() + "Italic Text" + ANSIColorizer.reset())

    # Ensure all changes are reset
    print(ANSIColorizer.reset())


if __name__ == "__main__":
    main()
