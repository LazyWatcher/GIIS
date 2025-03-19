import time


def hermite_basis(t):
    h1 = 2 * t ** 3 - 3 * t ** 2 + 1
    h2 = -2 * t ** 3 + 3 * t ** 2
    h3 = t ** 3 - 2 * t ** 2 + t
    h4 = t ** 3 - t ** 2
    return h1, h2, h3, h4


def draw_hermite_curve(canvas, P0, P1, T0, T1, debug=False):
    dt = 0.01
    t = 0.0
    while t <= 1.0:
        h1, h2, h3, h4 = hermite_basis(t)
        x = h1 * P0[0] + h2 * P1[0] + h3 * T0[0] + h4 * T1[0]
        y = h1 * P0[1] + h2 * P1[1] + h3 * T0[1] + h4 * T1[1]
        plot_pixel(canvas, int(round(x)), int(round(y)), debug)
        t += dt


def plot_pixel(canvas, x, y, debug):
    canvas.create_rectangle(x, y, x + 1, y + 1, fill="black", outline="black")
    if debug:
        canvas.update()
        time.sleep(0.01)



