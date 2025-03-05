import time


def draw_parabola(canvas, vx, vy, a, debug=False):
    canvas_width = int(canvas.winfo_width())
    R = canvas_width // 2
    for x in range(vx - R, vx + R + 1):
        y = int(round(vy + a * ((x - vx) ** 2)))
        canvas.create_rectangle(x, y, x + 1, y + 1, fill="black", outline="black")
        if debug:
            canvas.update()
            time.sleep(0.01)


