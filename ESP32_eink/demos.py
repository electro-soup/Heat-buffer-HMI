
#demo to generate Sierpinsky carpet, written with help of chatGPT
width, height = 400, 300

def calculate_max_depth_and_size(width, height, min_size):
    depth = 0
    size = min(width, height)
    while size % 3 == 0 and size // 3 >= min_size:
        size //= 3
        depth += 1
    size *= 3**depth  # Powrót do pełnej wielkości dywanu
    return depth, size

def draw_sierpinski_carpet(framebuffer, x, y, size, depth, max_depth):
    if depth > max_depth or size < 5:
        return

    new_size = size // 3

    # Tylko dwa kolory używane do rysowania kwadratów (biały i czerwony), tło jest czarne
    color = ['red', 'white']
    color_name = color[depth % 2]  # Przełączanie między czerwonym a białym

    # Rysuj środkowy kwadrat
    framebuffer.rect(x + new_size, y + new_size, new_size, new_size, color_name, fill=True)

    if new_size >= 5:
        for i in range(3):
            for j in range(3):
                # Pomiń rysowanie środkowego kwadratu
                if i == 1 and j == 1:
                    continue
                draw_sierpinski_carpet(framebuffer, x + i * new_size, y + j * new_size, new_size, depth + 1, max_depth)

# Ustawienie początkowe całego ekranu na czarne tło
framebuffer.fill('black')

# Obliczanie głębokości rekursji i maksymalnego rozmiaru
max_depth, full_size = calculate_max_depth_and_size(width, height, 5)

# Ustawienie pozycji początkowej, aby dywan był wyśrodkowany
start_x = (width - full_size) // 2
start_y = (height - full_size) // 2


# Rozpocznij rysowanie dywanu
draw_sierpinski_carpet(framebuffer, start_x, start_y, full_size, 5, 7) 