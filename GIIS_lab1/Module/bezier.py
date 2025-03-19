import time


def draw_bezier_curve(canvas, P0, P1, P2, P3, debug=False):
    dt = 0.01
    t = 0.0
    while t <= 1.0:
        x = ((1 - t) ** 3 * P0[0] +
             3 * t * (1 - t) ** 2 * P1[0] +
             3 * t ** 2 * (1 - t) * P2[0] +
             t ** 3 * P3[0])
        y = ((1 - t) ** 3 * P0[1] +
             3 * t * (1 - t) ** 2 * P1[1] +
             3 * t ** 2 * (1 - t) * P2[1] +
             t ** 3 * P3[1])

        plot_pixel(canvas, int(round(x)), int(round(y)), debug)
        t += dt


def plot_pixel(canvas, x, y, debug):
    canvas.create_rectangle(x, y, x + 1, y + 1, fill="black", outline="black")
    if debug:
        canvas.update()
        time.sleep(0.01)



