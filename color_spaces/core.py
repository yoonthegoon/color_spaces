from abc import ABC, abstractclassmethod, abstractmethod, abstractproperty

D65 = 0.95047, 1.00000, 1.08883


class BaseColorSpace(ABC):
    """Base class for color spaces."""

    @abstractmethod
    def __init__(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def __new__(cls, *args, **kwargs) -> "BaseColorSpace":
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass


class ColorSpace(BaseColorSpace):
    """Abstract class for color spaces."""

    @abstractproperty
    def XYZ(cls) -> "XYZ":
        """Convert to XYZ from the color space."""
        pass

    @abstractclassmethod
    def from_XYZ(cls, XYZ: "XYZ") -> "ColorSpace":
        """Convert from XYZ to the color space."""
        pass


class XYZ(BaseColorSpace):
    def __init__(self, X: float, Y: float, Z: float) -> None:
        self.X = X
        self.Y = Y
        self.Z = Z

    def __new__(cls, X: float, Y: float, Z: float) -> "XYZ":
        if not all(0 <= i for i in (X, Y, Z)):
            raise ValueError("XYZ values must be between 0 and 1.")

        return super().__new__(cls)

    @classmethod
    def from_Lab(cls, Lab: "Lab") -> "XYZ":
        X = D65[0] * cls.f((Lab.L + 16) / 116 + Lab.a / 500)
        Y = D65[1] * cls.f((Lab.L + 16) / 116)
        Z = D65[2] * cls.f((Lab.L + 16) / 116 - Lab.b / 200)
        return cls(X, Y, Z)

    @classmethod
    def from_Luv(cls, Luv: "Luv") -> "XYZ":
        u = Luv.u / (13 * Luv.L) + cls.u(*D65)
        v = Luv.v / (13 * Luv.L) + cls.v(*D65)

        if Luv.L > 8:
            Y = D65[1] * ((Luv.L + 16) / 116) ** 3

        else:
            Y = D65[1] * Luv.L * ((3 / 29) ** 3)

        X = Y * 9 * u / (4 * v)
        Z = Y * (12 - 3 * u - 20 * v) / (4 * v)
        return cls(X, Y, Z)

    @classmethod
    def from_sRGB(cls, sRGB: "sRGB") -> "XYZ":
        R, G, B = sRGB.linear[:]

        X = 0.4124564 * R + 0.3575761 * G + 0.1804375 * B
        Y = 0.2126729 * R + 0.7151522 * G + 0.0721750 * B
        Z = 0.0193339 * R + 0.1191920 * G + 0.9503041 * B
        return cls(X, Y, Z)

    @classmethod
    def from_xyY(cls, xyY: "xyY") -> "XYZ":
        if xyY.y == 0:
            return cls(0, 0, 0)

        X = (xyY.x / xyY.y) * xyY.Y
        Y = xyY.Y
        Z = ((1 - xyY.x - xyY.y) / xyY.y) * xyY.Y
        return cls(X, Y, Z)

    @property
    def Lab(self) -> "Lab":
        return Lab.from_XYZ(self)

    @property
    def Luv(self) -> "Luv":
        return Luv.from_XYZ(self)

    @property
    def sRGB(self) -> "sRGB":
        return sRGB.from_XYZ(self)

    @property
    def xyY(self) -> "xyY":
        return xyY.from_XYZ(self)

    def __getitem__(self, key: int) -> float:
        return (self.X, self.Y, self.Z)[key]

    def __repr__(self) -> str:
        return f"XYZ({self.X}, {self.Y}, {self.Z})"


class Lab(ColorSpace):
    def __init__(self, L: float, a: float, b: float) -> None:
        self.L = L
        self.a = a
        self.b = b

    def __new__(cls, L: float, a: float, b: float) -> "Lab":
        if not 0 <= L <= 100:
            raise ValueError("L must be between 0 and 100.")

        # TODO: Check a and b values

        return super().__new__(cls)

    @classmethod
    def from_XYZ(cls, XYZ: XYZ) -> "Lab":
        L = 116 * cls._f(XYZ.Y / D65[1]) - 16
        a = 500 * (cls._f(XYZ.X / D65[0]) - cls._f(XYZ.Y / D65[1]))
        b = 200 * (cls._f(XYZ.Y / D65[1]) - cls._f(XYZ.Z / D65[2]))
        return cls(L, a, b)

    @staticmethod
    def _f(t: float) -> float:
        if t > (6 / 29) ** 3:
            return t ** (1 / 3)

        return (1 / 3) * ((29 / 6) ** 2) * t + (4 / 29)

    @property
    def XYZ(self) -> XYZ:
        return XYZ.from_Lab(self)

    def f(self, t: float) -> float:
        if t > 6 / 29:
            return t**3

        return (3 * (6 / 29) ** 2) * (t - 4 / 29)

    def __repr__(self) -> str:
        return f"Lab({self.L}, {self.a}, {self.b})"

    def __getitem__(self, key: int) -> float:
        return (self.L, self.a, self.b)[key]


class Luv(ColorSpace):
    def __init__(self, L: float, u: float, v: float) -> None:
        self.L = L
        self.u = u
        self.v = v

    def __new__(cls, L: float, u: float, v: float) -> "Luv":
        if not 0 <= L <= 100:
            raise ValueError("L must be between 0 and 100.")

        # TODO: Check u and v values

        return super().__new__(cls)

    @classmethod
    def from_XYZ(cls, XYZ: XYZ) -> "Luv":
        if XYZ.Y / D65[1] > (6 / 29) ** 3:
            L = 116 * (XYZ.Y / D65[1]) ** (1 / 3) - 16

        else:
            L = (29 / 3) ** 3 * (XYZ.Y / D65[1])

        u = 13 * L * (cls.u(XYZ[:]) - cls.u(*D65))
        v = 13 * L * (cls.v(XYZ[:]) - cls.v(*D65))
        return cls(L, u, v)

    @staticmethod
    def u(X: float, Y: float, Z: float) -> float:
        return 4 * X / (X + 15 * Y + 3 * Z)

    @staticmethod
    def v(X: float, Y: float, Z: float) -> float:
        return 9 * Y / (X + 15 * Y + 3 * Z)

    @property
    def XYZ(self) -> XYZ:
        return XYZ.from_Luv(self)

    def __repr__(self) -> str:
        return f"Luv({self.L}, {self.u}, {self.v})"


class sRGB(ColorSpace):
    def __init__(self, R: float, G: float, B: float) -> None:
        self.R = R
        self.G = G
        self.B = B

    def __new__(cls, R: float, G: float, B: float) -> "sRGB":
        if not all(0 <= i <= 1 for i in (R, G, B)):
            raise ValueError("sRGB values must be between 0 and 1.")

        return super().__new__(cls)

    @classmethod
    def from_XYZ(cls, XYZ: XYZ) -> "sRGB":
        R = 3.2404542 * XYZ.X - 1.5371385 * XYZ.Y - 0.4985314 * XYZ.Z
        G = -0.9692660 * XYZ.X + 1.8760108 * XYZ.Y + 0.0415560 * XYZ.Z
        B = 0.0556434 * XYZ.X - 0.2040259 * XYZ.Y + 1.0572252 * XYZ.Z
        return cls(R, G, B)._gamma_expanded()

    @property
    def linear(self) -> "sRGB":
        return self._gamma_corrected()

    @property
    def XYZ(self) -> XYZ:
        return XYZ.from_sRGB(self)

    def __repr__(self) -> str:
        return f"sRGB({self.R}, {self.G}, {self.B})"

    def _gamma_corrected(self) -> "sRGB":
        raise NotImplementedError  # TODO: Implement gamma correction

    def _gamma_expanded(self) -> "sRGB":
        raise NotImplementedError  # TODO: Implement gamma expansion


class xyY(ColorSpace):
    def __init__(self, x: float, y: float, Y: float) -> None:
        self.x = x
        self.y = y
        self.Y = Y

    def __new__(cls, x: float, y: float, Y: float) -> "xyY":
        if not all(0 <= i <= 1 for i in (x, y, Y)):
            raise ValueError("xyY values must be between 0 and 1.")

        return super().__new__(cls)

    @classmethod
    def from_XYZ(cls, XYZ: XYZ) -> "xyY":
        if XYZ.X + XYZ.Y + XYZ.Z == 0:
            return cls(*D65[:2], 0)

        x = XYZ.X / (XYZ.X + XYZ.Y + XYZ.Z)
        y = XYZ.Y / (XYZ.X + XYZ.Y + XYZ.Z)
        return cls(x, y, XYZ.Y)

    @property
    def XYZ(self) -> XYZ:
        return XYZ.from_xyY(self)

    def __repr__(self) -> str:
        return f"xyY({self.x}, {self.y}, {self.Y})"
