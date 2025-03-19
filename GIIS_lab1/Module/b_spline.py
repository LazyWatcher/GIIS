import time


def bspline_basis(t):
    B0 = ((1 - t) ** 3) / 6.0
    B1 = (3 * t ** 3 - 6 * t ** 2 + 4) / 6.0
    B2 = (-3 * t ** 3 + 3 * t ** 2 + 3 * t + 1) / 6.0
    B3 = (t ** 3) / 6.0
    return B0, B1, B2, B3

def draw_bspline_curve(canvas, control_points, debug=False):
    dt = 0.01
    n = len(control_points)
    for i in range(n - 3):
        t = 0.0
        while t <= 1.0:
            B0, B1, B2, B3 = bspline_basis(t)
            x = (B0 * control_points[i][0] +
                 B1 * control_points[i + 1][0] +
                 B2 * control_points[i + 2][0] +
                 B3 * control_points[i + 3][0])
            y = (B0 * control_points[i][1] +
                 B1 * control_points[i + 1][1] +
                 B2 * control_points[i + 2][1] +
                 B3 * control_points[i + 3][1])
            plot_pixel(canvas, int(round(x)), int(round(y)), debug)
            t += dt


def plot_pixel(canvas, x, y, debug):
    canvas.create_rectangle(x, y, x + 1, y + 1, fill="black", outline="black")
    if debug:
        canvas.update()
        time.sleep(0.01)



