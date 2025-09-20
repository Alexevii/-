import pygame
from math import *
import time

class Point:
    def __init__(self, x: float, y: float, z: float = 0) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, a: "Point") -> "Point":
        return Point(self.x + a.x, self.y + a.y, self.z + a.z)

    def __radd__(self, a: "Point") -> "Point":
        return Point(self.x + a.x, self.y + a.y, self.z + a.z)

    def __sub__(self, a: "Point") -> "Point":
        return Point(self.x - a.x, self.y - a.y, self.z - a.z)

    def __rsub__(self, a: "Point") -> "Point":
        return Point(a.x - self.x, a.y - self.y, a.z - self.z)

    def __mul__(self, a: int | float) -> "Point":
        return Point(self.x * a, self.y * a, self.z * a)

    def __rmul__(self, a: int | float) -> "Point":
        return Point(self.x * a, self.y * a, self.z * a)

    def __truediv__(self, a: int | float) -> "Point":
        return Point(self.x / a, self.y / a, self.z / a)

    def __rtruediv__(self, a: int | float) -> "Point":
        return Point(a / self.x, a / self.y, a / self.z)

    def __repr__(self) -> str:
        return '(' + str(self.x) + ", " + str(self.y) + ", " + str(self.z) + ')'

    def dist(self, p2: "Point" = None) -> float:
        if p2 == None:
            return (self.x**2 + self.y**2 + self.z**2)**.5
        else:
            return ((self.x - p2.x)**2 + (self.y - p2.y)**2 + (self.z - p2.z)**2)**.5

class Basis:
    def __init__(self, b1: Point, b2: Point, b3: Point = Point(0, 0)) -> None:
        self.b1 = b1
        self.b2 = b2
        self.b3 = b3

class Slider:
    def __init__(self, p1: tuple[int], p2: tuple[int], min_value: float, max_value: float,
                 value: float, slider_radius: float, thumb_radius: float, empty_slider_color: pygame.Color, full_slider_color: pygame.Color,
                 thumb_color: pygame.Color) -> None:
        self.p1 = p1
        self.p2 = p2
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.slider_radius = slider_radius
        self.thumb_radius = thumb_radius
        self.full_slider_color = full_slider_color
        self.empty_slider_color = empty_slider_color
        self.thumb_color = thumb_color

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, self.full_slider_color, self.p1, self.slider_radius)
        pygame.draw.circle(surface, self.empty_slider_color, self.p2, self.slider_radius)

        d = ((self.p1[0] - self.p2[0])**2 + (self.p1[1] - self.p2[1])**2)**.5
        c = (self.slider_radius * (self.p1[1] - self.p2[1]) / d, self.slider_radius * (self.p2[0] - self.p1[0]) / d)

        v = (self.value - self.min_value) / (self.max_value - self.min_value)
        thumb = ((self.p2[0] - self.p1[0]) * v + self.p1[0], (self.p2[1] - self.p1[1]) * v + self.p1[1])

        pygame.draw.polygon(surface, self.full_slider_color, ((self.p1[0] + c[0], self.p1[1] + c[1]),
                                                               (self.p1[0] - c[0], self.p1[1] - c[1]),
                                                               (thumb[0] - c[0], thumb[1] - c[1]),
                                                               (thumb[0] + c[0], thumb[1] + c[1])))

        pygame.draw.polygon(surface, self.empty_slider_color, ((thumb[0] + c[0], thumb[1] + c[1]),
                                                               (thumb[0] - c[0], thumb[1] - c[1]),
                                                               (self.p2[0] - c[0], self.p2[1] - c[1]),
                                                               (self.p2[0] + c[0], self.p2[1] + c[1])))

        pygame.draw.circle(surface, self.thumb_color, thumb, self.thumb_radius)

    def is_thumb(self, cord: tuple[int]) -> bool:
        v = (self.value - self.min_value) / (self.max_value - self.min_value)
        thumb = ((self.p2[0] - self.p1[0]) * v + self.p1[0], (self.p2[1] - self.p1[1]) * v + self.p1[1])

        return (cord[0] - thumb[0])**2 + (cord[1] - thumb[1])**2 <= self.thumb_radius**2

    def get_value(self, cord: tuple[int]) -> float:
        dist = ((self.p1[0] - self.p2[0])**2 + (self.p1[1] - self.p2[1])**2)**.5
        b1 = ((self.p1[0] - self.p2[0]) / dist, (self.p1[1] - self.p2[1]) / dist)
        b2 = ((self.p2[1] - self.p1[1]) / dist, (self.p1[0] - self.p2[0]) / dist)

        return min(max(((self.p2[0] - cord[0]) * b2[1] + (self.p2[1] - cord[1]) * b1[1]) / dist + 1, 0), 1) * (self.max_value - self.min_value) + self.min_value

def main():
    global WIDTH
    global HEIGHT

    pygame.init()
    pygame.display.init()

    sizes = pygame.display.get_desktop_sizes()[0]
    WIDTH = sizes[0]
    HEIGHT = sizes[1]

    src_surface = pygame.display.set_mode((WIDTH, HEIGHT))
    drw_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    font = pygame.font.Font(None, 48)

    run = True

    points = []

    for z in range(10):
        for y in range(10):
            for x in range(10):
                points.append(Point(x / 10_000 + .001, y / 10_000 + .001, z / 10_000 + .001))

    sigma = 10
    r = 28
    b = 8/3
    camera = Point(-1, -70, 25)
    center = Point(-1, 0, 25)
    speed = 50
    PPR = 500                   # Pixel Per Rotate

    delta = 0.001
    speed_simulation = 1
    focus = 0
    keys = [False, False, False]
    fps = 0
    fps_time = time.time()
    counter_of_frames = 0
    alpha = 100
    hide = 0

    sliders = [Slider((50, HEIGHT - 50), (50, HEIGHT - 400), 1, 25, sigma, 25, 40, (127, 127, 127), (191, 191, 191), (255, 255, 255)),
               Slider((150, HEIGHT - 50), (150, HEIGHT - 400), 1, 100, r, 25, 40, (127, 127, 127), (191, 191, 191), (255, 255, 255)),
               Slider((250, HEIGHT - 50), (250, HEIGHT - 400), 0, 5, b, 25, 40, (127, 127, 127), (191, 191, 191), (255, 255, 255)),
               Slider((WIDTH - 50, HEIGHT - 50), (WIDTH - 600, HEIGHT - 50), 0, 3, speed_simulation, 25, 40, (127, 127, 127), (191, 191, 191), (255, 255, 255)),
               Slider((WIDTH - 50, 50), (WIDTH - 600, 50), 0, 100, alpha, 25, 40, (127, 127, 127), (191, 191, 191), (255, 255, 255))]

    while run:
        start_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    keys[1] = True
                if event.key == pygame.K_LCTRL:
                    keys[2] = True
                if event.key == pygame.K_r:
                    points = []
                    for z in range(10):
                        for y in range(10):
                            for x in range(10):
                                points.append(Point(x / 10_000 + .001, y / 1_000 + .001, z / 1_000 + .001))
                    sliders[0].value = 10
                    sliders[1].value = 28
                    sliders[2].value = 8/3
                    sliders[3].value = 1
                if event.key == pygame.K_h:
                    hide = (hide + 1) % 3
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    keys[1] = False
                if event.key == pygame.K_LCTRL:
                    keys[2] = False
        click = pygame.mouse.get_pressed()[0]
        if click and not keys[0]:
            cord = pygame.mouse.get_pos()
            for i in range(len(sliders)):
                if sliders[i].is_thumb(cord):
                    focus = i
                    break
            else:
                focus = -1
            keys[0] = True
        elif not click:
            keys[0] = False

        m = pygame.mouse.get_rel()
        if keys[0]:
            if focus == -1:
                a = m[0] / PPR
                camera = basis_transformation(Point(camera.x, camera.y, camera.z),
                                            Basis(Point(cos(a), sin(a)), Point(-sin(a), cos(a)), Point(0, 0, 1)))

                vec1 = center - camera
                a = m[1] / PPR * vec1.dist()
                vec2 = Point(center.y - camera.y, camera.x - center.x)
                result = get_third_vector(vec2 / vec2.dist(), vec1 / vec1.dist()) * a
                result = (result + camera) / (result + camera).dist(center) * camera.dist(center)
                if abs((result.z - center.z) / Point(result.x, result.y).dist(Point(center.x, center.y))) < 10:
                    camera = result
            else:
                sliders[focus].value = sliders[focus].get_value(pygame.mouse.get_pos())

            sigma = sliders[0].value
            r = sliders[1].value
            b = sliders[2].value
            speed_simulation = sliders[3].value
            alpha = sliders[4].value

        if keys[1]:
            a = camera.dist(center)
            if a > 5:
                camera = a / (a + speed * delta) * (camera - center) + center
        if keys[2]:
            a = camera.dist(center)
            camera = a / (a - speed * delta) * (camera - center) + center

        for i in range(len(points)):
            points[i] = iteration(points[i], delta * speed_simulation, sigma, r, b)

        draw_frame(drw_surface, points, camera, center, sliders, fps, font, sigma, r, b, speed_simulation, alpha, hide)
        src_surface.blit(drw_surface, (0, 0))
        pygame.display.flip()
        drw_surface.fill((0, 0, 0, alpha))

        delta = time.time() - start_time

        if time.time() - fps_time >= 1:
            fps_time = time.time()
            fps = counter_of_frames
            counter_of_frames = 0
        else:
            counter_of_frames += 1

    pygame.quit()

def draw_frame(surface: pygame.Surface, points: list[Point], cord: Point, center: Point, sliders: list[Slider],
               fps: int, font: pygame.font.Font, sigma: float, r: float, b: float, speed_simulation: float, alpha: float, hide: bool):
    viewing_angle = 90
    focus = tan(pi * (1/2 - viewing_angle / 360))

    rotate1 = Basis(Point(cord.y - center.y, center.x - cord.x) / Point(center.y - cord.y, cord.x - center.x).dist(),
                   get_third_vector(Point(cord.y - center.y, center.x - cord.x) / Point(center.y - cord.y, cord.x - center.x).dist(), Point(0, 0, 1)),
                   Point(0, 0, 1))

    cen2 = basis_transformation(center - cord, rotate1) + cord
    rotate2 = Basis(Point(1, 0, 0),
                    (cen2 - cord) / (cen2 - cord).dist(),
                    get_third_vector((cen2 - cord) / (cen2 - cord).dist(), Point(1, 0, 0)))

    for i in range(len(points)):
        p = basis_transformation(points[i] - cord, rotate1) + cord
        p = basis_transformation(p - cord, rotate2) + cord
        x = p.x
        y = p.y
        z = p.z

        if y - cord.y < 0: continue

        try:
            d = ((points[i].x - cord.x)**2 + (points[i].y - cord.y)**2 + (points[i].z - cord.z)**2)**.5
        finally:
            scale = -focus / d
            size = 250 / d

            if size > 1:
                pygame.draw.circle(surface,
                                (255, 255, 255),
                                (WIDTH - ((x - cord.x) * scale + 1/2) * HEIGHT - (WIDTH - HEIGHT)/2, HEIGHT - ((z - cord.z) * scale + 1/2) * HEIGHT),
                                size)
            else:
                surface.set_at((int(WIDTH - ((x - cord.x) * scale + 1/2) * HEIGHT - (WIDTH - HEIGHT)/2), int(HEIGHT - ((z - cord.z) * scale + 1/2) * HEIGHT)), (255, 255, 255))

    if hide == 0:
        for i in sliders:
            i.draw(surface)

        text = font.render("σ", True, (255, 255, 255))
        surface.blit(text, (50 - text.get_width()//2, HEIGHT - 500 - text.get_height()//2))
        text = font.render(str(round(sigma, 2)), True, (255, 255, 255))
        surface.blit(text, (50 - text.get_width()//2, HEIGHT - 450 - text.get_height()//2))

        text = font.render("r", True, (255, 255, 255))
        surface.blit(text, (150 - text.get_width()//2, HEIGHT - 500 - text.get_height()//2))
        text = font.render(str(round(r, 2)), True, (255, 255, 255))
        surface.blit(text, (150 - text.get_width()//2, HEIGHT - 450 - text.get_height()//2))

        text = font.render("b", True, (255, 255, 255))
        surface.blit(text, (250 - text.get_width()//2, HEIGHT - 500 - text.get_height()//2))
        text = font.render(str(round(b, 2)), True, (255, 255, 255))
        surface.blit(text, (250 - text.get_width()//2, HEIGHT - 450 - text.get_height()//2))

        text = font.render("speed simulation", True, (255, 255, 255))
        surface.blit(text, (WIDTH - 175 - text.get_width()//2, HEIGHT - 110 - text.get_height()//2))
        text = font.render(str(int(100 * speed_simulation)) + '%', True, (255, 255, 255))
        surface.blit(text, (WIDTH - 380 - text.get_width()//2, HEIGHT - 110 - text.get_height()//2))

        text = font.render("alpha", True, (255, 255, 255))
        surface.blit(text, (WIDTH - 100 - text.get_width()//2, 110 - text.get_height()//2))
        text = font.render(str(int(alpha)), True, (255, 255, 255))
        surface.blit(text, (WIDTH - 200 - text.get_width()//2, 110 - text.get_height()//2))

    if hide != 2:
        surface.blit(font.render("FPS: " + str(fps), True, (255, 255, 255)), (0, 0))

def iteration(p: Point, delta: float, sigma: float, r: float, b: float) -> Point:
    result = Point(p.x + (sigma * (p.y - p.x)) * delta,
                   p.y + (p.x * (r - p.z) - p.y) * delta,
                   p.z + (p.x * p.y - b * p.z) * delta)
    c = int(result.dist(p) // 0.5)

    if c > 1:
        result = p
        for i in range(c):
            result = Point(result.x + (sigma * (result.y - result.x)) * delta / c,
                           result.y + (result.x * (r - result.z) - result.y) * delta / c,
                           result.z + (result.x * result.y - b * result.z) * delta / c)

    return result

def basis_transformation(p: Point, b: Basis) -> Point:
    return b.b1 * p.x + b.b2 * p.y + b.b3 * p.z

def get_third_vector(p1: Point, p2: Point) -> Point:
    return Point(p1.y * p2.z - p2.y * p1.z,
                 p1.z * p2.x - p2.z * p1.x,
                 p1.x * p2.y - p2.x * p1.y)

main()
