import time


def draw_circle(canvas, cx, cy, radius, debug=False):
    x = 0
    y = radius
    d = 1 - radius

    while x <= y:
        plot_pixel(canvas, cx + x, cy + y, debug)
        plot_pixel(canvas, cx + y, cy + x, debug)
        plot_pixel(canvas, cx - x, cy + y, debug)
        plot_pixel(canvas, cx - y, cy + x, debug)
        plot_pixel(canvas, cx - x, cy - y, debug)
        plot_pixel(canvas, cx - y, cy - x, debug)
        plot_pixel(canvas, cx + x, cy - y, debug)
        plot_pixel(canvas, cx + y, cy - x, debug)

        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1


def plot_pixel(canvas, x, y, debug):
    canvas.create_rectangle(x, y, x + 1, y + 1, fill="black", outline="black")
    if debug:
        canvas.update()
        time.sleep(0.01)



