import math
import time


def _ipart(x):
    return math.floor(x)
def _round(x):
    return _ipart(x + 0.5)
def _fpart(x):
    return x - math.floor(x)
def _rfpart(x):
    return 1 - _fpart(x)

def _plot(canvas, x, y, intensity, debug=False):
    intensity = max(0, min(1, intensity))
    gray_value = int((1 - intensity) * 255)
    color = f"#{gray_value:02x}{gray_value:02x}{gray_value:02x}"
    canvas.create_rectangle(x, y, x + 1, y + 1, fill=color, outline=color)

    if debug:
        canvas.update()
        time.sleep(0.05)


def draw_line(canvas, x0, y0, x1, y1, debug=False):
    steep = abs(y1 - y0) > abs(x1 - x0)

    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0
    gradient = dy / dx if dx != 0 else 1.0

    xend = _round(x0)
    yend = y0 + gradient * (xend - x0)
    xgap = _rfpart(x0 + 0.5)
    xpixel1 = xend
    ypixel1 = _ipart(yend)

    if steep:
        _plot(canvas, ypixel1, xpixel1, _rfpart(yend) * xgap, debug)
        _plot(canvas, ypixel1 + 1, xpixel1, _fpart(yend) * xgap, debug)
    else:
        _plot(canvas, xpixel1, ypixel1, _rfpart(yend) * xgap, debug)
        _plot(canvas, xpixel1, ypixel1 + 1, _fpart(yend) * xgap, debug)

    intery = yend + gradient
    xend = _round(x1)
    yend = y1 + gradient * (xend - x1)
    xgap = _fpart(x1 + 0.5)
    xpixel2 = xend
    ypixel2 = _ipart(yend)

    if steep:
        _plot(canvas, ypixel2, xpixel2, _rfpart(yend) * xgap, debug)
        _plot(canvas, ypixel2 + 1, xpixel2, _fpart(yend) * xgap, debug)
    else:
        _plot(canvas, xpixel2, ypixel2, _rfpart(yend) * xgap, debug)
        _plot(canvas, xpixel2, ypixel2 + 1, _fpart(yend) * xgap, debug)

    if steep:
        for x in range(xpixel1 + 1, xpixel2):
            y = _ipart(intery)
            _plot(canvas, y, x, _rfpart(intery), debug)
            _plot(canvas, y + 1, x, _fpart(intery), debug)
            intery += gradient
    else:
        for x in range(xpixel1 + 1, xpixel2):
            y = _ipart(intery)
            _plot(canvas, x, y, _rfpart(intery), debug)
            _plot(canvas, x, y + 1, _fpart(intery), debug)
            intery += gradient



