import time
import math


def draw_ellipse(canvas, cx, cy, rx, ry, debug=False):
    x = 0
    y = ry
    rx2 = rx * rx
    ry2 = ry * ry
    d1 = ry2 - (rx2 * ry) + (0.25 * rx2)
    dx = 2 * ry2 * x
    dy = 2 * rx2 * y

    while dx < dy:
        plot_pixel(canvas, cx + x, cy + y, debug)
        plot_pixel(canvas, cx - x, cy + y, debug)
        plot_pixel(canvas, cx + x, cy - y, debug)
        plot_pixel(canvas, cx - x, cy - y, debug)

        if d1 < 0:
            x += 1
            dx = 2 * ry2 * x
            d1 = d1 + dx + ry2
        else:
            x += 1
            y -= 1
            dx = 2 * ry2 * x
            dy = 2 * rx2 * y
            d1 = d1 + dx - dy + ry2


    d2 = (ry2) * ((x + 0.5) ** 2) + (rx2) * ((y - 1) ** 2) - (rx2 * ry2)
    while y >= 0:
        plot_pixel(canvas, cx + x, cy + y, debug)
        plot_pixel(canvas, cx - x, cy + y, debug)
        plot_pixel(canvas, cx + x, cy - y, debug)
        plot_pixel(canvas, cx - x, cy - y, debug)

        if d2 > 0:
            y -= 1
            dy = 2 * rx2 * y
            d2 = d2 - dy + rx2
        else:
            y -= 1
            x += 1
            dx = 2 * ry2 * x
            dy = 2 * rx2 * y
            d2 = d2 + dx - dy + rx2


def plot_pixel(canvas, x, y, debug):
    canvas.create_rectangle(x, y, x + 1, y + 1, fill="black", outline="black")
    if debug:
        canvas.update()
        time.sleep(0.02)



