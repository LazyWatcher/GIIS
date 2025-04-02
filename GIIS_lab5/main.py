import tkinter as tk
from tkinter import messagebox, Menu, Checkbutton, Button, BooleanVar, Frame, Scrollbar
import math
import time


def cross_product(p1, p2, p3):
    return (p2[0] - p1[0]) * (p3[1] - p1[1]) - \
           (p2[1] - p1[1]) * (p3[0] - p1[0])

def distance_sq(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

def get_intersection_point(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2; x3, y3 = p3; x4, y4 = p4
    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denominator == 0:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
    return None

class RasterGrid:
    EMPTY = 0; BOUNDARY = 1; FILLED = 2
    FILL_COLOR = "lightblue"; BOUNDARY_COLOR = "black"
    def __init__(self, canvas, width, height):
        self.canvas = canvas; self.width = int(width); self.height = int(height)
        self.grid = [[self.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        self.pixel_rects = {}
    def clear(self):
        self.grid = [[self.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        for pixel_id in self.pixel_rects.values(): self.canvas.delete(pixel_id)
        self.pixel_rects = {}
    def _bresenham_line(self, x0, y0, x1, y1):
        points = []; dx = abs(x1 - x0); dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1; sy = 1 if y0 < y1 else -1; err = dx + dy
        while True:
            points.append((int(x0), int(y0)))
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 >= dy: err += dy; x0 += sx
            if e2 <= dx: err += dx; y0 += sy
        return points
    def draw_polygon_boundaries(self, polygon_points):
        if not polygon_points or len(polygon_points) < 2: return
        for i in range(len(polygon_points)):
            p1 = polygon_points[i]; p2 = polygon_points[(i + 1) % len(polygon_points)]
            x0, y0 = int(p1[0]), int(p1[1]); x1, y1 = int(p2[0]), int(p2[1])
            line_pixels = self._bresenham_line(x0, y0, x1, y1)
            for x, y in line_pixels: self.set_pixel(x, y, self.BOUNDARY, draw=False)
    def set_pixel(self, x, y, state, draw=True):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = state
            if draw:
                coord = (x, y)
                if coord in self.pixel_rects: self.canvas.delete(self.pixel_rects[coord])
                color = ""
                if state == self.BOUNDARY: color = self.BOUNDARY_COLOR
                elif state == self.FILLED: color = self.FILL_COLOR
                if color:
                    pixel_id = self.canvas.create_rectangle(x, y, x + 1, y + 1, fill=color, outline="")
                    self.pixel_rects[coord] = pixel_id
                    self.canvas.tag_raise("polygon_edge"); self.canvas.tag_raise("point")
    def get_pixel(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height: return self.grid[y][x]
        return None

class PolygonEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Графический редактор полигонов (с заполнением)")
        self.master.geometry("900x750")
        self.points = []; self.polygon_edges = []; self.hull_edges = []
        self.normal_lines = []; self.line_points = []; self.current_line_id = None
        self.intersection_points_ids = []; self.seed_point = None; self.mode = "polygon"
        self.debug_mode = BooleanVar(value=False); self.debug_generator = None; self.debug_delay = 0.1
        top_frame = Frame(master); top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.next_step_button = Button(top_frame, text="Следующий шаг ▶", state=tk.DISABLED, command=self.execute_next_debug_step)
        self.next_step_button.pack(side=tk.RIGHT, padx=5)
        self.canvas = tk.Canvas(master, bg="white", cursor="crosshair")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.canvas.bind("<Button-1>", self.handle_click); self.canvas.bind("<Button-3>", self.finalize_polygon)
        self.canvas.bind("<B1-Motion>", self.handle_drag); self.canvas.bind("<ButtonRelease-1>", self.handle_release)
        self.master.update_idletasks()
        canvas_width = self.canvas.winfo_width(); canvas_height = self.canvas.winfo_height()
        if canvas_width < 10 or canvas_height < 10: canvas_width, canvas_height = 800, 600
        self.raster_grid = RasterGrid(self.canvas, canvas_width, canvas_height)
        self.status_var = tk.StringVar(); self.status_bar = tk.Label(master, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X); self.update_status()
        self.menu_bar = Menu(master); master.config(menu=self.menu_bar)

        file_menu = Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Очистить холст", command=self.clear_canvas); file_menu.add_separator(); file_menu.add_command(label="Выход", command=master.quit)
        polygon_menu = Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Полигон", menu=polygon_menu)
        polygon_menu.add_command(label="Рисовать полигон", command=lambda: self.set_mode("polygon")); polygon_menu.add_command(label="Проверить на выпуклость", command=self.check_convexity)
        polygon_menu.add_command(label="Показать внутренние нормали", command=self.show_normals); polygon_menu.add_command(label="Проверить точку внутри полигона", command=lambda: self.set_mode("point_in_polygon"))
        fill_menu = Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Заполнение", menu=fill_menu)
        fill_menu.add_command(label="Алгоритм растровой развертки с упоряд. списком ребер", command=self.fill_scanline_edge_table); fill_menu.add_command(label="Алгоритм растровой развертки со списком активных ребер", command=self.fill_scanline_active_edge)
        fill_menu.add_command(label="Простой с затравкой", command=self.fill_seed_simple); fill_menu.add_command(label="Построчный с затравкой", command=self.fill_seed_scanline)
        fill_menu.add_separator(); fill_menu.add_checkbutton(label="Режим отладки", variable=self.debug_mode, command=self.toggle_debug_mode)
        hull_menu = Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Выпуклая оболочка", menu=hull_menu)
        hull_menu.add_command(label="Обход Грэхема", command=self.build_hull_graham); hull_menu.add_command(label="Метод Джарвиса", command=self.build_hull_jarvis)
        line_menu = Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Линия", menu=line_menu)
        line_menu.add_command(label="Рисовать линию", command=lambda: self.set_mode("line")); line_menu.add_command(label="Найти пересечения с полигоном", command=self.find_intersections)


    def handle_click(self, event):
        x, y = event.x, event.y
        if self.mode == "polygon":
            self.points.append((x, y))
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="blue", outline="blue", tags=("point", "polygon_element"))
            if len(self.points) > 1:
                p1, p2 = self.points[-2], self.points[-1]
                edge_id = self.canvas.create_line(p1, p2, fill="black", tags=("polygon_edge", "polygon_element"))
                self.polygon_edges.append(edge_id)
            self.update_status()
        elif self.mode == "line":
             self.clear_fill_elements()
             if not self.line_points:
                self.line_points.append((x, y))
                self.current_line_id = self.canvas.create_line(x, y, x, y, fill="red", dash=(4, 2), tags="current_line")
             self.update_status()
        elif self.mode == "point_in_polygon": self.check_point_in_polygon((x, y))
        elif self.mode == "seed_fill_select":
            self.seed_point = (int(x), int(y))
            self.canvas.delete("seed_point_marker")
            self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="green", outline="black", tags="seed_point_marker")
            messagebox.showinfo("Затравка выбрана", f"Точка затравки: {self.seed_point}. Теперь снова выберите алгоритм заполнения с затравкой из меню.")
            self.set_mode("polygon")
            self.update_status()

    def handle_drag(self, event):
        if self.mode == "line" and self.line_points and self.current_line_id:
            start_x, start_y = self.line_points[0]
            self.canvas.coords(self.current_line_id, start_x, start_y, event.x, event.y)

    def handle_release(self, event):
        if self.mode == "line" and len(self.line_points) == 1 and self.current_line_id:
            x, y = event.x, event.y
            if self.line_points[0] != (x, y): self.line_points.append((x, y)); self.finalize_line()
            else: self.canvas.delete(self.current_line_id); self.current_line_id = None; self.line_points = []; self.update_status()

    def finalize_polygon(self, event=None):
        if self.mode == "polygon" and len(self.points) >= 3:
            if not self.is_polygon_closed():
                p1, p2 = self.points[-1], self.points[0]
                edge_id = self.canvas.create_line(p1, p2, fill="black", tags=("polygon_edge", "polygon_element"))
                self.polygon_edges.append(edge_id); messagebox.showinfo("Полигон завершен", f"Полигон с {len(self.points)} вершинами создан."); self.update_status()
            else: messagebox.showinfo("Полигон", "Полигон уже был завершен.")
        elif self.mode == "polygon" and len(self.points) < 3: messagebox.showwarning("Недостаточно точек", "Для полигона нужно как минимум 3 точки.")

    def finalize_line(self):
        if self.current_line_id and len(self.line_points) == 2:
            self.canvas.itemconfig(self.current_line_id, fill="green", width=2, dash=(), tags=("line_segment"))
            messagebox.showinfo("Линия нарисована", f"Отрезок создан."); self.current_line_id = None; self.update_status()

    def set_mode(self, new_mode):
        self.mode = new_mode
        if self.mode != "line" and self.current_line_id: self.canvas.delete(self.current_line_id); self.current_line_id = None
        if self.debug_generator and self.mode != 'debug_step': self.stop_debugging()
        self.update_status()

    def update_status(self):
        status = f"Режим: {self.mode} | Точек полигона: {len(self.points)}"
        if self.line_points: status += f" | Отрезок: {'Да' if len(self.line_points) == 2 else 'Рисуется'}"
        if self.seed_point and self.mode != "seed_fill_select": status += f" | Затравка: {self.seed_point}"
        if self.debug_mode.get(): status += " | ОТЛАДКА АКТИВНА"
        if self.mode == "polygon": status += " (ЛКМ - точка, ПКМ - завершить)"
        elif self.mode == "line": status += " (ЛКМ/Перетащить - линия)"
        elif self.mode == "point_in_polygon": status += " (ЛКМ - проверить точку)"
        elif self.mode == "seed_fill_select": status += " (ЛКМ - выбрать точку затравки)"
        self.status_var.set(status)

    def clear_canvas(self):
        self.stop_debugging(); self.canvas.delete("all")
        self.points = []; self.polygon_edges = []; self.hull_edges = []
        self.normal_lines = []; self.line_points = []; self.current_line_id = None
        self.intersection_points_ids = []
        self.clear_fill_elements()
        if hasattr(self, 'raster_grid'): self.raster_grid.clear()
        self.set_mode("polygon"); messagebox.showinfo("Очистка", "Холст очищен.")

    def clear_fill_elements(self):
         if hasattr(self, 'raster_grid'): self.raster_grid.clear()
         self.canvas.delete("seed_point_marker")
         self.canvas.delete("debug_highlight")
         self.stop_debugging()

    def clear_visuals(self, clear_hull=True, clear_normals=True, clear_intersections=True):
        if clear_hull: self.canvas.delete("hull_edge"); self.hull_edges = []
        if clear_normals: self.canvas.delete("normal"); self.normal_lines = []
        if clear_intersections: self.canvas.delete("intersection"); self.intersection_points_ids = []
        if hasattr(self, 'raster_grid'): self.raster_grid.clear()
        self.canvas.delete("debug_highlight")
        self.stop_debugging()

    def is_polygon_closed(self):
        if len(self.points) < 3: return False
        p_last = self.points[-1]; p_first = self.points[0]
        for edge_id in self.polygon_edges:
             if "polygon_edge" in self.canvas.gettags(edge_id):
                try:
                    coords = self.canvas.coords(edge_id); epsilon = 1e-6
                    p1_match = abs(coords[0]-p_last[0]) < epsilon and abs(coords[1]-p_last[1]) < epsilon
                    p2_match = abs(coords[2]-p_first[0]) < epsilon and abs(coords[3]-p_first[1]) < epsilon
                    p1_rev_match = abs(coords[0]-p_first[0]) < epsilon and abs(coords[1]-p_first[1]) < epsilon
                    p2_rev_match = abs(coords[2]-p_last[0]) < epsilon and abs(coords[3]-p_last[1]) < epsilon
                    if (p1_match and p2_match) or (p1_rev_match and p2_rev_match): return True
                except tk.TclError: continue
        return False
    def is_convex(self):
        n = len(self.points);
        if n < 3: return False;
        sign = 0
        for i in range(n):
            p1, p2, p3 = self.points[i], self.points[(i + 1) % n], self.points[(i + 2) % n]
            cp = cross_product(p1, p2, p3)
            if cp != 0:
                if sign == 0: sign = 1 if cp > 0 else -1
                elif (cp > 0 and sign < 0) or (cp < 0 and sign > 0): return False
        return True
    def check_convexity(self):
        if len(self.points) < 3: messagebox.showwarning("Проверка выпуклости", "Нужно как минимум 3 точки."); return
        if not self.is_polygon_closed(): messagebox.showwarning("Проверка выпуклости", "Пожалуйста, завершите полигон (ПКМ)."); return
        if self.is_convex(): messagebox.showinfo("Проверка выпуклости", "Полигон выпуклый.")
        else: messagebox.showinfo("Проверка выпуклости", "Полигон невыпуклый (вогнутый).")
    def calculate_normals(self):
        n = len(self.points);
        if n < 3: return None;
        normals = []
        for i in range(n):
            p1, p2 = self.points[i], self.points[(i + 1) % n]
            dx = p2[0] - p1[0]; dy = p2[1] - p1[1]; nx, ny = -dy, dx
            length = math.sqrt(nx**2 + ny**2)
            if length > 0: nx /= length; ny /= length
            else: nx, ny = 0, 0
            mid_x = (p1[0] + p2[0]) / 2; mid_y = (p1[1] + p2[1]) / 2
            normals.append(((mid_x, mid_y), (nx, ny)))
        return normals
    def show_normals(self):
        self.clear_visuals(clear_hull=False, clear_normals=True, clear_intersections=False)
        if len(self.points) < 3: messagebox.showwarning("Показ нормалей", "Нужно как минимум 3 точки."); return
        if not self.is_polygon_closed(): messagebox.showwarning("Показ нормалей", "Пожалуйста, завершите полигон (ПКМ)."); return
        if not self.is_convex(): messagebox.showwarning("Показ нормалей", "Расчет и отображение нормалей корректно работают для выпуклых полигонов.")
        normals_data = self.calculate_normals();
        if not normals_data: return
        normal_length = 30
        for midpoint, normal_vec in normals_data:
            start_x, start_y = midpoint; end_x = start_x + normal_vec[0] * normal_length; end_y = start_y + normal_vec[1] * normal_length
            line_id = self.canvas.create_line(start_x, start_y, end_x, end_y, fill="purple", arrow=tk.LAST, tags=("normal"))
            self.normal_lines.append(line_id)

    def _draw_hull(self, hull_points):
        self.clear_visuals(clear_hull=True, clear_normals=True, clear_intersections=True)
        if not hull_points or len(hull_points) < 2: return
        for i in range(len(hull_points)):
            p1, p2 = hull_points[i], hull_points[(i + 1) % len(hull_points)]
            edge_id = self.canvas.create_line(p1, p2, fill="red", width=2, tags="hull_edge")
            self.hull_edges.append(edge_id)
        for p in hull_points: self.canvas.create_oval(p[0]-4, p[1]-4, p[0]+4, p[1]+4, outline="red", width=1, tags="hull_edge")
        messagebox.showinfo("Выпуклая оболочка", f"Выпуклая оболочка построена ({len(hull_points)} вершин).")
    def build_hull_graham(self):
        points = self.points[:]; n = len(points)
        if n < 3: messagebox.showwarning("Обход Грэхема", "Нужно как минимум 3 точки."); return
        min_y_idx = 0
        for i in range(1, n):
            if points[i][1] < points[min_y_idx][1] or \
               (points[i][1] == points[min_y_idx][1] and points[i][0] < points[min_y_idx][0]): min_y_idx = i
        points[0], points[min_y_idx] = points[min_y_idx], points[0]; pivot = points[0]
        def polar_angle(p): angle = math.atan2(p[1] - pivot[1], p[0] - pivot[0]); dist = distance_sq(pivot, p); return (angle, dist)
        points[1:] = sorted(points[1:], key=polar_angle); hull = [points[0], points[1]]
        for i in range(2, n):
            while len(hull) >= 2 and cross_product(hull[-2], hull[-1], points[i]) <= 0: hull.pop()
            hull.append(points[i])
        self._draw_hull(hull)
    def build_hull_jarvis(self):
        points = self.points[:]; n = len(points)
        if n < 3: messagebox.showwarning("Метод Джарвиса", "Нужно как минимум 3 точки."); return
        leftmost_idx = 0
        for i in range(1, n):
            if points[i][0] < points[leftmost_idx][0] or \
               (points[i][0] == points[leftmost_idx][0] and points[i][1] < points[leftmost_idx][1]): leftmost_idx = i
        hull = []; current_idx = leftmost_idx; iter_count = 0
        while True:
            hull.append(points[current_idx]); next_idx = (current_idx + 1) % n
            for i in range(n):
                orientation = cross_product(points[current_idx], points[next_idx], points[i])
                if orientation < 0: next_idx = i
                elif orientation == 0:
                    dist_sq_next = distance_sq(points[current_idx], points[next_idx]); dist_sq_i = distance_sq(points[current_idx], points[i])
                    if dist_sq_i > dist_sq_next: next_idx = i
            current_idx = next_idx; iter_count += 1
            if current_idx == leftmost_idx or iter_count > n*n: break
        if iter_count > n*n: messagebox.showerror("Ошибка Джарвиса", "Превышено число итераций."); return
        self._draw_hull(hull)

    def find_intersections(self):
        self.clear_visuals(clear_hull=False, clear_normals=False, clear_intersections=True)
        if len(self.points) < 3 or not self.is_polygon_closed(): messagebox.showwarning("Поиск пересечений", "Сначала завершите полигон (ПКМ)."); return
        if len(self.line_points) != 2: messagebox.showwarning("Поиск пересечений", "Сначала нарисуйте линию."); return
        line_start, line_end = self.line_points; intersections_found = []
        n = len(self.points)
        for i in range(n):
            poly_p1, poly_p2 = self.points[i], self.points[(i + 1) % n]
            intersection_pt = get_intersection_point(line_start, line_end, poly_p1, poly_p2)
            if intersection_pt:
                intersections_found.append(intersection_pt); x, y = intersection_pt
                pt_id = self.canvas.create_oval(x-4, y-4, x+4, y+4, fill="orange", outline="black", tags=("intersection"))
                self.intersection_points_ids.append(pt_id)
        if intersections_found: messagebox.showinfo("Поиск пересечений", f"Найдено {len(intersections_found)} пересечений.")
        else: messagebox.showinfo("Поиск пересечений", "Пересечений линии с полигоном не найдено.")
    def check_point_in_polygon(self, point_to_check):
        if len(self.points) < 3 or not self.is_polygon_closed(): messagebox.showwarning("Проверка точки", "Сначала завершите полигон (ПКМ)."); self.set_mode("polygon"); return
        x, y = point_to_check; n = len(self.points); inside = False
        self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="cyan", outline="black", tags="temp_point")
        p1x, p1y = self.points[0]
        for i in range(n + 1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y: xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters: inside = not inside
            p1x, p1y = p2x, p2y
        if inside: messagebox.showinfo("Проверка точки", f"Точка {point_to_check} ВНУТРИ полигона.")
        else: messagebox.showinfo("Проверка точки", f"Точка {point_to_check} СНАРУЖИ полигона.")
        self.master.after(2000, lambda: self.canvas.delete("temp_point")); self.set_mode("polygon")

    def toggle_debug_mode(self):
        if self.debug_mode.get():
             if self.debug_generator: self.next_step_button.config(state=tk.NORMAL)
             else: self.next_step_button.config(state=tk.DISABLED)
        else: self.stop_debugging()
        self.update_status()
    def start_debugging(self, generator):
        if not self.debug_mode.get():
            try:
                for _ in generator: pass
                self.canvas.delete("seed_point_marker")
            except Exception as e: messagebox.showerror("Ошибка выполнения", f"Произошла ошибка: {e}")
            finally: self.stop_debugging()
            return
        self.debug_generator = generator; self.next_step_button.config(state=tk.NORMAL); self.update_status()
    def execute_next_debug_step(self):
        if self.debug_generator:
            try: next(self.debug_generator); self.master.update()
            except StopIteration:
                self.stop_debugging(); messagebox.showinfo("Отладка завершена", "Алгоритм выполнен.")
                self.canvas.delete("seed_point_marker")
            except Exception as e: messagebox.showerror("Ошибка отладки", f"Произошла ошибка на шаге: {e}"); self.stop_debugging()
        else: self.stop_debugging()
    def stop_debugging(self):
        self.debug_generator = None; self.next_step_button.config(state=tk.DISABLED)
        self.canvas.delete("debug_highlight"); self.update_status()
    def highlight_scanline(self, y):
        self.canvas.delete("debug_highlight_scanline")
        if self.debug_mode.get():
             w = self.canvas.winfo_width()
             self.canvas.create_line(0, y, w, y, fill="orange", width=1, dash=(4, 4), tags=("debug_highlight", "debug_highlight_scanline"))
    def highlight_AEL(self, AEL, y):
        self.canvas.delete("debug_highlight_ael")
        if self.debug_mode.get():
            for edge in AEL:
                 x = int(edge['x_intersection'])
                 self.canvas.create_line(x-5, y, x+5, y, fill="red", width=3, tags=("debug_highlight", "debug_highlight_ael"))

    def _prepare_fill(self):

        if hasattr(self, 'raster_grid'): self.raster_grid.clear()
        self.canvas.delete("debug_highlight")
        self.stop_debugging()
        self.master.update_idletasks()
        cw = self.canvas.winfo_width(); ch = self.canvas.winfo_height()
        if cw > 1 and ch > 1 and (self.raster_grid.width != cw or self.raster_grid.height != ch):
             self.raster_grid = RasterGrid(self.canvas, cw, ch)

        self.raster_grid.draw_polygon_boundaries(self.points)
        return True

    def fill_scanline_edge_table(self):
        if len(self.points) < 3: messagebox.showwarning("Заполнение", "Нужно как минимум 3 точки."); return
        if not self.is_polygon_closed(): messagebox.showwarning("Заполнение", "Пожалуйста, завершите полигон (ПКМ)."); return
        if not self._prepare_fill(): return
        self.seed_point = None
        self.canvas.delete("seed_point_marker")
        self.start_debugging(self._scanline_et_generator())

    def _scanline_et_generator(self):
        polygon = self.points; n = len(polygon)
        if n == 0: return
        min_y = int(min(p[1] for p in polygon)); max_y = int(max(p[1] for p in polygon))
        edge_table = {y: [] for y in range(min_y, max_y + 1)}
        for i in range(n):
            p1, p2 = polygon[i], polygon[(i + 1) % n]
            y1, y2 = int(p1[1]), int(p2[1]); x1, x2 = int(p1[0]), int(p2[0])
            if y1 == y2: continue
            if y1 < y2: ymin, ymax, x_at_ymin = y1, y2, x1
            else: ymin, ymax, x_at_ymin = y2, y1, x2
            inv_slope = (x2 - x1) / (y2 - y1) if y1 != y2 else 0
            edge_data = {'y_max': ymax, 'x_intersection': float(x_at_ymin), 'inv_slope': inv_slope}
            if ymin in edge_table: edge_table[ymin].append(edge_data)
        active_edge_list = []
        for y in range(min_y, max_y + 1):
            if y in edge_table:
                for edge in edge_table[y]: active_edge_list.append(edge.copy())
            active_edge_list = [edge for edge in active_edge_list if edge['y_max'] != y]
            active_edge_list.sort(key=lambda edge: edge['x_intersection'])
            if self.debug_mode.get(): self.highlight_scanline(y); self.highlight_AEL(active_edge_list, y); yield
            for i in range(0, len(active_edge_list), 2):
                if i + 1 < len(active_edge_list):
                    x_start = math.ceil(active_edge_list[i]['x_intersection'])
                    x_end = math.floor(active_edge_list[i+1]['x_intersection'])
                    for x in range(x_start, x_end + 1):
                         current_state = self.raster_grid.get_pixel(x, y)
                         if current_state == RasterGrid.EMPTY: self.raster_grid.set_pixel(x, y, RasterGrid.FILLED)
            if self.debug_mode.get():
                 if self.debug_delay > 0: time.sleep(self.debug_delay / 2)
            for edge in active_edge_list: edge['x_intersection'] += edge['inv_slope']


    def fill_scanline_active_edge(self):
        if len(self.points) < 3: messagebox.showwarning("Заполнение", "Нужно как минимум 3 точки."); return
        if not self.is_polygon_closed(): messagebox.showwarning("Заполнение", "Пожалуйста, завершите полигон (ПКМ)."); return
        if not self._prepare_fill(): return
        self.seed_point = None
        self.canvas.delete("seed_point_marker")
        self.start_debugging(self._scanline_et_generator())
    def fill_seed_simple(self):
        if not self.seed_point:
            if len(self.points) < 3: messagebox.showwarning("Заполнение", "Сначала нарисуйте полигон (минимум 3 точки)."); return
            if not self.is_polygon_closed(): messagebox.showwarning("Заполнение", "Пожалуйста, завершите полигон (ПКМ)."); return
            self.set_mode("seed_fill_select")
            messagebox.showinfo("Заполнение", "Выберите точку затравки (ЛКМ внутри полигона).")
            return

        else:
            if len(self.points) < 3 or not self.is_polygon_closed():
                 messagebox.showwarning("Заполнение", "Ошибка: полигон не готов для заливки."); self.seed_point = None; self.canvas.delete("seed_point_marker"); return

            if not self._prepare_fill():
                self.seed_point = None; self.canvas.delete("seed_point_marker"); return

            seed_x, seed_y = self.seed_point
            seed_state = self.raster_grid.get_pixel(seed_x, seed_y)
            if seed_state == RasterGrid.BOUNDARY:
                messagebox.showwarning("Заполнение", "Точка затравки на границе. Выберите другую точку."); self.seed_point = None; self.canvas.delete("seed_point_marker"); return
            if seed_state is None:
                messagebox.showwarning("Заполнение", "Точка затравки вне холста."); self.seed_point = None; self.canvas.delete("seed_point_marker"); return
            if seed_state == RasterGrid.FILLED:
                 messagebox.showinfo("Заполнение", "Область уже заполнена."); self.seed_point = None; self.canvas.delete("seed_point_marker"); return

            current_seed = self.seed_point
            self.start_debugging(self._boundary_fill4_generator(current_seed[0], current_seed[1]))


    def _boundary_fill4_generator(self, x_seed, y_seed):
        width = self.raster_grid.width; height = self.raster_grid.height
        boundary_color = RasterGrid.BOUNDARY; fill_color = RasterGrid.FILLED; empty_color = RasterGrid.EMPTY
        stack = [(x_seed, y_seed)]
        while stack:
            x, y = stack.pop()
            if not (0 <= x < width and 0 <= y < height): continue
            current_state = self.raster_grid.get_pixel(x, y)
            if current_state != empty_color: continue
            self.raster_grid.set_pixel(x, y, fill_color)
            neighbors = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            for nx, ny in neighbors: stack.append((nx, ny))
            if self.debug_mode.get():
                self.canvas.delete("debug_highlight_pixel")
                self.canvas.create_rectangle(x, y, x + 1, y + 1, fill="yellow", outline="", tags=("debug_highlight", "debug_highlight_pixel"))
                yield


    def fill_seed_scanline(self):
        if not self.seed_point:
            if len(self.points) < 3: messagebox.showwarning("Заполнение", "Сначала нарисуйте полигон (минимум 3 точки)."); return
            if not self.is_polygon_closed(): messagebox.showwarning("Заполнение", "Пожалуйста, завершите полигон (ПКМ)."); return
            self.set_mode("seed_fill_select")
            messagebox.showinfo("Заполнение", "Выберите точку затравки (ЛКМ внутри полигона).")
            return

        else:
            if len(self.points) < 3 or not self.is_polygon_closed():
                 messagebox.showwarning("Заполнение", "Ошибка: полигон не готов для заливки."); self.seed_point = None; self.canvas.delete("seed_point_marker"); return

            if not self._prepare_fill():
                self.seed_point = None; self.canvas.delete("seed_point_marker"); return

            seed_x, seed_y = self.seed_point
            seed_state = self.raster_grid.get_pixel(seed_x, seed_y)
            if seed_state == RasterGrid.BOUNDARY:
                messagebox.showwarning("Заполнение", "Точка затравки на границе. Выберите другую точку."); self.seed_point = None; self.canvas.delete("seed_point_marker"); return
            if seed_state is None:
                messagebox.showwarning("Заполнение", "Точка затравки вне холста."); self.seed_point = None; self.canvas.delete("seed_point_marker"); return
            if seed_state == RasterGrid.FILLED:
                 messagebox.showinfo("Заполнение", "Область уже заполнена."); self.seed_point = None; self.canvas.delete("seed_point_marker"); return

            current_seed = self.seed_point
            self.start_debugging(self._scanline_seed_fill_generator(current_seed[0], current_seed[1]))


    def _scanline_seed_fill_generator(self, x_seed, y_seed):
        width = self.raster_grid.width; height = self.raster_grid.height
        boundary_state = RasterGrid.BOUNDARY; fill_state = RasterGrid.FILLED; empty_state = RasterGrid.EMPTY
        stack = [(x_seed, y_seed)]
        while stack:
            x, y = stack.pop()
            x_left = x
            while x_left >= 0 and self.raster_grid.get_pixel(x_left, y) == empty_state:
                self.raster_grid.set_pixel(x_left, y, fill_state); x_left -= 1
            x_left += 1
            x_right = x + 1
            while x_right < width and self.raster_grid.get_pixel(x_right, y) == empty_state:
                self.raster_grid.set_pixel(x_right, y, fill_state); x_right += 1
            x_right -= 1
            if self.debug_mode.get():
                self.canvas.delete("debug_highlight_segment")
                self.canvas.create_line(x_left, y + 0.5, x_right + 1, y + 0.5, fill="green", width=2, tags=("debug_highlight", "debug_highlight_segment"))
                yield
            for check_y in [y - 1, y + 1]:
                 if 0 <= check_y < height:
                    in_segment = False
                    for check_x in range(x_left, x_right + 1):
                        current_state = self.raster_grid.get_pixel(check_x, check_y)
                        if current_state == empty_state:
                            if not in_segment: stack.append((check_x, check_y)); in_segment = True
                        else: in_segment = False
            if self.debug_mode.get():
                 if self.debug_delay > 0: time.sleep(self.debug_delay / 2)


if __name__ == "__main__":
    root = tk.Tk()
    app = PolygonEditor(root)
    root.mainloop()
