from color_spaces.core import LCh, Luv, sRGB


def ansi(base_C: float, base_h: float):
    normal = (0.05 * 1.05) ** 0.5 - 0.05
    black = (normal + 0.05) / 4.5 - 0.05
    white = (normal + 0.05) * 4.5 - 0.05
    dim = (black + 0.05) * 3 - 0.05
    bright = (white + 0.05) / 3 - 0.05
    black, dim, normal, bright, white = map(
        lambda x: x * 100, (black, dim, normal, bright, white)
    )
    ansi_colors = {
        "black": LCh(black, base_C, base_h).sRGB(Luv),
        "red": LCh(normal, 180, 15).sRGB(Luv),
        "green": LCh(normal, 180, 135).sRGB(Luv),
        "yellow": LCh(normal, 180, 75).sRGB(Luv),
        "blue": LCh(normal, 180, 255).sRGB(Luv),
        "magenta": LCh(normal, 180, 315).sRGB(Luv),
        "cyan": LCh(normal, 180, 195).sRGB(Luv),
        "white": LCh(bright, base_C, base_h).sRGB(Luv),
        "bright_black": LCh(dim, base_C, base_h).sRGB(Luv),
        "bright_red": LCh(bright, 180, 15).sRGB(Luv),
        "bright_green": LCh(bright, 180, 135).sRGB(Luv),
        "bright_yellow": LCh(bright, 180, 75).sRGB(Luv),
        "bright_blue": LCh(bright, 180, 255).sRGB(Luv),
        "bright_magenta": LCh(bright, 180, 315).sRGB(Luv),
        "bright_cyan": LCh(bright, 180, 195).sRGB(Luv),
        "bright_white": LCh(white, base_C, base_h).sRGB(Luv),
    }
    return ansi_colors


def main():
    base = sRGB(
        *(1 - c for c in sRGB(0.2126729, 0.7151522, 0.0721750)._gamma_expanded())
    )
    for name, color in ansi(15, base.XYZ.Luv.LCh.h).items():
        print(f"{color.hex} {name}")
        print(color.XYZ.Luv.LCh)
        print()


if __name__ == "__main__":
    main()
