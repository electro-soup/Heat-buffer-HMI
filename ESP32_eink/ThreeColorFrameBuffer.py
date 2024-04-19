class ThreeColorFrameBuffer:
    def __init__(self, width, height, framebuffer_black, framebuffer_red):
        self.framebuffer_black = framebuffer_black
        self.framebuffer_red = framebuffer_red
        self.width = width
        self.height = height

    def fill(self, color_name):
        if color_name == "black":
            self.framebuffer_black.fill(0)
            self.framebuffer_red.fill(1)
        elif color_name == "white":
            self.framebuffer_black.fill(1)
            self.framebuffer_red.fill(1)
        elif color_name == "red":
            self.framebuffer_black.fill(1)
            self.framebuffer_red.fill(0)

    def pixel(self, x, y, color_name):
        if color_name == "black":
            self.framebuffer_black.pixel(x, y, 0)
            self.framebuffer_red.pixel(x, y, 1)
        elif color_name == "white":
            self.framebuffer_black.pixel(x, y, 1)
            self.framebuffer_red.pixel(x, y, 1)
        elif color_name == "red":
            self.framebuffer_black.pixel(x, y, 1)
            self.framebuffer_red.pixel(x, y, 0)

    def hline(self, x, y, width, color_name):
        if color_name == "black":
            self.framebuffer_black.hline(x, y, width, 0)
            self.framebuffer_red.hline(x, y, width, 1)
        elif color_name == "white":
            self.framebuffer_black.hline(x, y, width, 1)
            self.framebuffer_red.hline(x, y, width, 1)
        elif color_name == "red":
            self.framebuffer_black.hline(x, y, width, 1)
            self.framebuffer_red.hline(x, y, width, 0)

    def vline(self, x, y, height, color_name):
        if color_name == "black":
            self.framebuffer_black.vline(x, y, height, 0)
            self.framebuffer_red.vline(x, y, height, 1)
        elif color_name == "white":
            self.framebuffer_black.vline(x, y, height, 1)
            self.framebuffer_red.vline(x, y, height, 1)
        elif color_name == "red":
            self.framebuffer_black.vline(x, y, height, 1)
            self.framebuffer_red.vline(x, y, height, 0)

    def line(self, x1, y1, x2, y2, color_name):
        if color_name == "black":
            self.framebuffer_black.line(x1, y1, x2, y2, 0)
            self.framebuffer_red.line(x1, y1, x2, y2, 1)
        elif color_name == "white":
            self.framebuffer_black.line(x1, y1, x2, y2, 1)
            self.framebuffer_red.line(x1, y1, x2, y2, 1)
        elif color_name == "red":
            self.framebuffer_black.line(x1, y1, x2, y2, 1)
            self.framebuffer_red.line(x1, y1, x2, y2, 0)

  
    def ellipse(self, x, y, rx, ry, color_name, fill=False):
        if color_name == "black":
             self.framebuffer_black.ellipse(x, y, rx, ry, 0, fill)
             self.framebuffer_red.ellipse(x, y, rx, ry, 1, fill)
        elif color_name == "white":
             self.framebuffer_black.ellipse(x, y, rx, ry, 1, fill)
             self.framebuffer_red.ellipse(x, y, rx, ry, 1, fill)
        elif color_name == "red":
             self.framebuffer_black.ellipse(x, y, rx, ry, 1, fill)
             self.framebuffer_red.ellipse(x, y, rx, ry, 0, fill)

    def rect(self, x, y, width, height, color_name, fill=False):
        if color_name == "black":
            self.framebuffer_black.rect(x, y, width, height, 0, fill)
            self.framebuffer_red.rect(x, y, width, height, 1, fill)
        elif color_name == "white":
            self.framebuffer_black.rect(x, y, width, height, 1, fill)
            self.framebuffer_red.rect(x, y, width, height, 1, fill)
        elif color_name == "red":
            self.framebuffer_black.rect(x, y, width, height, 1, fill)
            self.framebuffer_red.rect(x, y, width, height, 0, fill)

    def text(self, string, x, y, color_name):
        if color_name == "black":
            self.framebuffer_black.text(string, x, y, 0)  # 0 zazwyczaj oznacza kolor czarny
            self.framebuffer_red.text(string, x, y, 1)    # 1 zazwyczaj oznacza kolor biały lub przezroczysty
        elif color_name == "white":
            self.framebuffer_black.text(string, x, y, 1)
            self.framebuffer_red.text(string, x, y, 1)
        elif color_name == "red":
            self.framebuffer_black.text(string, x, y, 1)
            self.framebuffer_red.text(string, x, y, 0)  # 0 oznacza tutaj kolor czerwony
