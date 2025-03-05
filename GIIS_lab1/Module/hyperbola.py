import math
import time


def draw_hyperbola(canvas, cx, cy, a, b, debug=False):
    t = 0.0
    dt = 0.01
    t_max = 1.0

    while t <= t_max:
        x_offset = a * math.cosh(t)
        y_offset = b * math.sinh(t)
        plot_pixel(canvas, cx + x_offset, cy + y_offset, debug)
        plot_pixel(canvas, cx + x_offset, cy - y_offset, debug)
        plot_pixel(canvas, cx - x_offset, cy + y_offset, debug)
        plot_pixel(canvas, cx - x_offset, cy - y_offset, debug)
        t += dt

def plot_pixel(canvas, x, y, debug):
    canvas.create_rectangle(x, y, x + 1, y + 1, fill="black", outline="black")
    if debug:
        canvas.update()
        time.sleep(0.02)


