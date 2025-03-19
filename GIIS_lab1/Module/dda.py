import time

def draw_line(canvas, x0, y0, x1, y1, debug=False):

    dx = x1 - x0
    dy = y1 - y0

    steps = int(max(abs(dx), abs(dy)))
    if steps == 0:
        canvas.create_rectangle(round(x0), round(y0), round(x0) + 1, round(y0) + 1, fill="black", outline="black")
        return

    x_inc = dx / steps
    y_inc = dy / steps

    x, y = x0, y0

    for i in range(steps + 1):
        canvas.create_rectangle(round(x), round(y), round(x) + 1, round(y) + 1, fill="black", outline="black")

        if debug:
            canvas.update()
            time.sleep(0.05)

        x += x_inc
        y += y_inc



