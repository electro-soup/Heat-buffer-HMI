class ThreeColorFrameBuffer:
    def __init__(self, width, height, framebuffer_black, framebuffer_red):
        self.framebuffer_black = framebuffer_black
        self.framebuffer_red = framebuffer_red
        self.width = width
        self.height = height
        self.color_map = {
            "black": (0, 1),  # (wartość dla framebuffer_black, wartość dla framebuffer_red)
            "white": (1, 1),
            "red":   (1, 0)
        }

    def _apply_color(self, method_name, *args, color_name, fill=None, mode=None):
        if color_name not in self.color_map:
            raise ValueError("Unsupported color name")
        black_value, red_value = self.color_map[color_name]
        
        # Przygotowanie argumentów do wywołania metod na framebufferach
        black_args = args + (black_value,) + (fill,) if fill is not None else args + (black_value,)
        red_args = args + (red_value,) + (fill,) if fill is not None else args + (red_value,)
        
        # Wywołanie metod na odpowiednich framebufferach
        if mode is not None:
            getattr(self.framebuffer_black, method_name)(*black_args, mode)
            getattr(self.framebuffer_red, method_name)(*red_args, mode)
        else:
            getattr(self.framebuffer_black, method_name)(*black_args)
            getattr(self.framebuffer_red, method_name)(*red_args)

    def fill(self, color_name):
        self._apply_color("fill", color_name=color_name)

    def pixel(self, x, y, color_name):
        self._apply_color("pixel", x, y, color_name=color_name)

    def hline(self, x, y, width, color_name):
        self._apply_color("hline", x, y, width, color_name=color_name)

    def vline(self, x, y, height, color_name):
        self._apply_color("vline", x, y, height, color_name=color_name)

    def line(self, x1, y1, x2, y2, color_name):
        self._apply_color("line", x1, y1, x2, y2, color_name=color_name)

    def ellipse(self, x, y, rx, ry, color_name, fill=False, mode=0b1111):
        self._apply_color("ellipse", x, y, rx, ry, color_name=color_name, fill=fill, mode=mode)

    def rect(self, x, y, width, height, color_name, fill=False):
        self._apply_color("rect", x, y, width, height, color_name=color_name, fill=fill)

    def text(self, string, x, y, color_name):
        self._apply_color("text", string, x, y, color_name=color_name)
    
    def poly(self, x, y, coords, color_name, fill=False):
        self._apply_color("poly", x, y, coords, color_name=color_name, fill=fill)