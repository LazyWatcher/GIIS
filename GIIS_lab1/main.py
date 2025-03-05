import tkinter as tk
from tkinter import messagebox
import math
import Module.dda as dda
import Module.bresenham as bresenham
import Module.wu as wu
import Module.circle as circle
import Module.ellipse as ellipse
import Module.hyperbola as hyperbola
import Module.parabola as parabola


selected_algorithm = None
debug_mode = False
start_point = None
scale_factor = 1.0
mode = "line"
def set_algorithm(algorithm_module):
    global selected_algorithm, start_point, mode
    selected_algorithm = algorithm_module
    start_point = None
    mode = "line"
    status_var.set("Выбран алгоритм: " + algorithm_module.__name__)

def set_curve(algorithm_module):
    global selected_algorithm, start_point, mode
    selected_algorithm = algorithm_module
    start_point = None
    mode = "curve"
    status_var.set("Выбран алгоритм: " + algorithm_module.__name__)

def toggle_debug():
    global debug_mode
    debug_mode = not debug_mode
    status = "ON" if debug_mode else "OFF"
    status_var.set(f"Отладочный режим: {status}")

def on_canvas_click(event):
    global start_point
    if selected_algorithm is None:
        messagebox.showwarning("Не выбран алгоритм", "Сначала выберите алгоритм построения из меню!")
        return

    x = int(round(event.x / scale_factor))
    y = int(round(event.y / scale_factor))

    if mode == "line":
        if start_point is None:
            start_point = (x, y)
            status_var.set(f"Начальная точка: {start_point}")
        else:
            end_point = (x, y)
            status_var.set(f"Отрезок: {start_point} -> {end_point}")
            selected_algorithm.draw_line(canvas, start_point[0], start_point[1],
                                         end_point[0], end_point[1], debug_mode)
            start_point = None

    elif mode == "curve":
        if start_point is None:
            start_point = (x, y)
            if selected_algorithm == circle:
                status_var.set(f"Центр окружности: {start_point}. Выберите точку на окружности.")
            elif selected_algorithm == ellipse:
                status_var.set(f"Центр эллипса: {start_point}. Выберите точку для определения полуосей rx и ry.")
            elif selected_algorithm == hyperbola:
                status_var.set(f"Центр гиперболы: {start_point}. Выберите точку для определения параметров a и b.")
            elif selected_algorithm == parabola:
                status_var.set(f"Вершина параболы: {start_point}. Выберите точку для определения параметра a.")
            else:
                status_var.set(f"Центр: {start_point}. Выберите вторую точку.")
        else:
            second_point = (x, y)
            if selected_algorithm == circle:
                dx = second_point[0] - start_point[0]
                dy = second_point[1] - start_point[1]
                radius = int(round(math.sqrt(dx*dx + dy*dy)))
                status_var.set(f"Окружность: центр {start_point}, радиус {radius}")
                selected_algorithm.draw_circle(canvas, start_point[0], start_point[1], radius, debug_mode)
            elif selected_algorithm == ellipse:
                rx = abs(second_point[0] - start_point[0])
                ry = abs(second_point[1] - start_point[1])
                status_var.set(f"Эллипс: центр {start_point}, rx {rx}, ry {ry}")
                selected_algorithm.draw_ellipse(canvas, start_point[0], start_point[1], rx, ry, debug_mode)
            elif selected_algorithm == hyperbola:
                a = abs(second_point[0] - start_point[0])
                b = abs(second_point[1] - start_point[1])
                status_var.set(f"Гипербола: центр {start_point}, a {a}, b {b}")
                selected_algorithm.draw_hyperbola(canvas, start_point[0], start_point[1], a, b, debug_mode)
            elif selected_algorithm == parabola:
                if second_point[0] == start_point[0]:
                    messagebox.showerror("Ошибка", "Невозможно определить параметр a, так как x-координаты совпадают.")
                else:
                    a_param = (second_point[1] - start_point[1]) / ((second_point[0] - start_point[0]) ** 2)
                    status_var.set(f"Парабола: вершина {start_point}, a = {a_param:.4f}")
                    selected_algorithm.draw_parabola(canvas, start_point[0], start_point[1], a_param, debug_mode)
            start_point = None

def zoom(factor, pivot_x=0, pivot_y=0):
    global scale_factor
    new_scale = scale_factor * factor
    canvas.scale("all", pivot_x, pivot_y, factor, factor)
    scale_factor = new_scale
    status_var.set(f"Масштаб: {scale_factor:.2f}")

def zoom_in():
    zoom(2.0, 0, 0)

def zoom_out():
    if scale_factor <= 1.0:
        return
    zoom(0.5, 0, 0)

def on_right_click(event):
    context_menu = tk.Menu(root, tearoff=0)
    context_menu.add_command(label="Увеличить", command=lambda: zoom(2.0, event.x, event.y))
    context_menu.add_command(label="Уменьшить", command=lambda: zoom(0.5, event.x, event.y))
    context_menu.post(event.x_root, event.y_root)

root = tk.Tk()
root.title("Элементарный графический редактор")
root.geometry("800x600")

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

line_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Отрезки", menu=line_menu)
line_menu.add_command(label="Алгоритм ЦДА", command=lambda: set_algorithm(dda))
line_menu.add_command(label="Алгоритм Брезенхэма", command=lambda: set_algorithm(bresenham))
line_menu.add_command(label="Алгоритм Ву", command=lambda: set_algorithm(wu))

curve_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Линии второго порядка", menu=curve_menu)
curve_menu.add_command(label="Окружность", command=lambda: set_curve(circle))
curve_menu.add_command(label="Эллипс", command=lambda: set_curve(ellipse))
curve_menu.add_command(label="Гипербола", command=lambda: set_curve(hyperbola))
curve_menu.add_command(label="Парабола", command=lambda: set_curve(parabola))

debug_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Отладка", menu=debug_menu)
debug_menu.add_command(label="Переключить отладочный режим", command=toggle_debug)

zoom_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Масштаб", menu=zoom_menu)
zoom_menu.add_command(label="Увеличить (Zoom In)", command=zoom_in)
zoom_menu.add_command(label="Уменьшить (Zoom Out)", command=zoom_out)

canvas = tk.Canvas(root, width=100, height=100, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind("<Button-1>", on_canvas_click)
canvas.bind("<Button-3>", on_right_click)

orig_create_rectangle = canvas.create_rectangle
orig_create_line = canvas.create_line

def create_rectangle_zoomed(x1, y1, x2, y2, *args, **kwargs):
    return orig_create_rectangle(x1 * scale_factor, y1 * scale_factor,
                                 x2 * scale_factor, y2 * scale_factor, *args, **kwargs)

def create_line_zoomed(*args, **kwargs):
    new_args = [coord * scale_factor for coord in args]
    return orig_create_line(*new_args, **kwargs)

canvas.create_rectangle = create_rectangle_zoomed
canvas.create_line = create_line_zoomed

status_var = tk.StringVar()
status_var.set("Выберите алгоритм построения")
status_bar = tk.Label(root, textvariable=status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
