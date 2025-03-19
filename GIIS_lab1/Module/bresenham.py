import time

def draw_line(canvas, x0, y0, x1, y1, debug=False):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        canvas.create_rectangle(x0, y0, x0 + 1, y0 + 1, fill="black", outline="black")
        if debug:
            canvas.update()
            time.sleep(0.05)

        if x0 == x1 and y0 == y1:
            break

        e2 = 2 * err

        if e2 > -dy:
            err -= dy
            x0 += sx

        if e2 < dx:
            err += dx
            y0 += sy



