from color_spaces.core import XYZ, LCh, Luv, sRGB


def ansi(base_C: float, base_h: float, max_C=120):
    def middle_lightness(l: float, d: float):
        return ((l + 0.05) * (d + 0.05)) ** 0.5 - 0.05

    def LCh_base(L: float):
        return LCh(L, base_C, base_h).sRGB(Luv)

    def LCh_color(L: float, R: float, G: float, B: float):
        return LCh(L, max_C, sRGB(R, G, B).XYZ.Luv.LCh.h).sRGB(Luv)

    normal = middle_lightness(0, 1)
    black = (normal + 0.05) / 3 - 0.05
    white = (normal + 0.05) * 3 - 0.05
    dim = middle_lightness(normal, black)
    bright = middle_lightness(normal, white)

    black, dim, normal, bright, white = map(
        lambda x: XYZ(0, x, 0).Luv.LCh.L, (black, dim, normal, bright, white)
    )

    ansi_colors = {
        "black": LCh_base(black),
        "red": LCh_color(normal, 1, 0, 0),
        "green": LCh_color(normal, 0, 1, 0),
        "yellow": LCh_color(normal, 1, 1, 0),
        "blue": LCh_color(normal, 0, 0, 1),
        "magenta": LCh_color(normal, 1, 0, 1),
        "cyan": LCh_color(normal, 0, 1, 1),
        "white": LCh_base(bright),
        "bright_black": LCh_base(dim),
        "bright_red": LCh_color(bright, 1, 0, 0),
        "bright_green": LCh_color(bright, 0, 1, 0),
        "bright_yellow": LCh_color(bright, 1, 1, 0),
        "bright_blue": LCh_color(bright, 0, 0, 1),
        "bright_magenta": LCh_color(bright, 1, 0, 1),
        "bright_cyan": LCh_color(bright, 0, 1, 1),
        "bright_white": LCh_base(white),
    }
    return ansi_colors


def main():
    base = sRGB(
        *(1 - c for c in sRGB(0.2126729, 0.7151522, 0.0721750)._gamma_expanded())
    )
    print(base.hex)
    print(base.XYZ.Luv.LCh)
    for name, color in ansi(15, base.XYZ.Luv.LCh.h).items():
        print(f"{color.hex} {name}")


if __name__ == "__main__":
    main()
