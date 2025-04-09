import tkinter as tk
from tkinter import messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import itertools
import math

EPSILON = 1e-10

class TriangulationResult:

    def __init__(self, points, simplices):
        self.points = np.asarray(points)
        self.simplices = np.asarray(simplices, dtype=int)
        self.neighbors = None

def calculate_circumcenter_radius_sq(p1, p2, p3):

    D = 2 * (p1[0] * (p2[1] - p3[1]) + p2[0] * (p3[1] - p1[1]) + p3[0] * (p1[1] - p2[1]))
    if abs(D) < EPSILON:
        return None, None

    p1_sq = np.sum(p1**2)
    p2_sq = np.sum(p2**2)
    p3_sq = np.sum(p3**2)

    Ux = (1 / D) * (p1_sq * (p2[1] - p3[1]) + p2_sq * (p3[1] - p1[1]) + p3_sq * (p1[1] - p2[1]))
    Uy = (1 / D) * (p1_sq * (p3[0] - p2[0]) + p2_sq * (p1[0] - p3[0]) + p3_sq * (p2[0] - p1[0]))

    center = np.array([Ux, Uy])
    radius_sq = np.sum((p1 - center)**2)
    return center, radius_sq

def is_in_circumcircle(p1, p2, p3, p_test):

    center, radius_sq = calculate_circumcenter_radius_sq(p1, p2, p3)
    if center is None:
        return False

    dist_sq = np.sum((p_test - center)**2)

    return dist_sq < radius_sq - EPSILON


def custom_delaunay(points_input):

    if not isinstance(points_input, np.ndarray):
        points_input = np.asarray(points_input)

    num_points = len(points_input)
    if num_points < 3:
        print("Предупреждение: Для триангуляции Делоне необходимо минимум 3 точки.")
        return None

    points = points_input.copy()

    min_coord = np.min(points, axis=0)
    max_coord = np.max(points, axis=0)
    delta = max_coord - min_coord

    delta[delta < EPSILON] = 1.0
    max_delta = np.max(delta)
    center = (min_coord + max_coord) / 2.0

    p_super1 = center + np.array([-20 * max_delta, -10 * max_delta])
    p_super2 = center + np.array([ 20 * max_delta, -10 * max_delta])
    p_super3 = center + np.array([ 0, 20 * max_delta])


    super_indices = [0, 1, 2]
    points_with_super = np.vstack((p_super1, p_super2, p_super3, points))
    triangles = [[0, 1, 2]]


    for i in range(num_points):
        point_idx = i + 3
        current_point = points_with_super[point_idx]

        bad_triangles_indices = []
        polygon_edges = []

        for tri_idx, tri_verts_indices in enumerate(triangles):
            v1 = points_with_super[tri_verts_indices[0]]
            v2 = points_with_super[tri_verts_indices[1]]
            v3 = points_with_super[tri_verts_indices[2]]


            if is_in_circumcircle(v1, v2, v3, current_point):
                bad_triangles_indices.append(tri_idx)
                polygon_edges.append(tuple(sorted((tri_verts_indices[0], tri_verts_indices[1]))))
                polygon_edges.append(tuple(sorted((tri_verts_indices[1], tri_verts_indices[2]))))
                polygon_edges.append(tuple(sorted((tri_verts_indices[2], tri_verts_indices[0]))))

        edge_counts = {}
        for edge in polygon_edges:
            edge_counts[edge] = edge_counts.get(edge, 0) + 1

        boundary_edges = [list(edge) for edge, count in edge_counts.items() if count == 1]

        for tri_idx in sorted(bad_triangles_indices, reverse=True):
            del triangles[tri_idx]

        for edge in boundary_edges:
            if edge[0] != point_idx and edge[1] != point_idx and edge[0] != edge[1]:
                 triangles.append([edge[0], edge[1], point_idx])

    final_triangles = []
    original_indices_map = {}
    count = 0
    for i in range(len(points_with_super)):
         if i not in super_indices:
             original_indices_map[i] = count
             count += 1

    for tri_verts_indices in triangles:
        if not any(idx in super_indices for idx in tri_verts_indices):
            try:
                corrected_indices = [original_indices_map[idx] for idx in tri_verts_indices]
                final_triangles.append(corrected_indices)
            except KeyError as e:
                 print(f"Ошибка: Не найден индекс {e} при коррекции симплексов.")


    if not final_triangles:
        print("Предупреждение: Не удалось построить ни одного финального треугольника.")
        return None

    return TriangulationResult(points_input, final_triangles)


def calculate_circumcenter(p1, p2, p3):
    center, _ = calculate_circumcenter_radius_sq(p1, p2, p3)
    return center

def _calculate_neighbors(tri):

    if tri is None or not hasattr(tri, 'simplices'):
        return None

    num_simplices = len(tri.simplices)
    if num_simplices == 0:
        tri.neighbors = np.empty((0, 3), dtype=int)
        return tri.neighbors

    neighbors = -np.ones((num_simplices, 3), dtype=int)
    edge_map = {}
    for i, s in enumerate(tri.simplices):
        if len(s) != 3:
            print(f"Ошибка: Симплекс {i} имеет не 3 вершины: {s}")
            continue
        if s[0] == s[1] or s[1] == s[2] or s[0] == s[2]:
             print(f"Предупреждение: Вырожденный симплекс {i}: {s}")
             continue

        edges_in_simplex = [tuple(sorted((s[0], s[1]))),
                            tuple(sorted((s[1], s[2]))),
                            tuple(sorted((s[2], s[0])))]
        for edge in edges_in_simplex:
            if edge not in edge_map:
                edge_map[edge] = []
            edge_map[edge].append(i)

    for i, s in enumerate(tri.simplices):
         if len(s) != 3 or s[0] == s[1] or s[1] == s[2] or s[0] == s[2]:
             continue

         edge_keys = [tuple(sorted((s[1], s[2]))),
                      tuple(sorted((s[2], s[0]))),
                      tuple(sorted((s[0], s[1])))]

         for j, edge_key in enumerate(edge_keys):
             tris_with_edge = edge_map.get(edge_key, [])
             for neighbor_idx in tris_with_edge:
                 if neighbor_idx != i:
                     neighbors[i, j] = neighbor_idx
                     break
    tri.neighbors = neighbors
    return neighbors


def construct_voronoi_from_delaunay(tri, plot_bounds):

    if tri is None or not hasattr(tri, 'simplices') or not hasattr(tri, 'points'):
         print("Ошибка: Некорректный объект триангуляции для построения Вороного.")
         return [], [], {}


    if not hasattr(tri, 'neighbors') or tri.neighbors is None:
        _calculate_neighbors(tri)
        if tri.neighbors is None:
             print("Ошибка: Не удалось вычислить соседей.")
             return [], [], {}
        print("Вычисление соседей завершено.")

    voronoi_finite_edges = []
    voronoi_infinite_rays = []
    circumcenters = {}

    for i, simplex in enumerate(tri.simplices):
        try:
            p1 = tri.points[simplex[0]]
            p2 = tri.points[simplex[1]]
            p3 = tri.points[simplex[2]]
            center = calculate_circumcenter(p1, p2, p3)
            if center is not None:
                circumcenters[i] = center
        except IndexError:
             print(f"Ошибка индекса при доступе к точкам для симплекса {i}: {simplex}. Max индекс точки: {len(tri.points)-1}")
             continue


    processed_pairs = set()
    for i, simplex in enumerate(tri.simplices):
        if i not in circumcenters: continue

        for j in range(3):
            neighbor_idx = tri.neighbors[i, j]

            if neighbor_idx != -1:
                pair = tuple(sorted((i, neighbor_idx)))
                if neighbor_idx in circumcenters and pair not in processed_pairs:
                    center1 = circumcenters[i]
                    center2 = circumcenters[neighbor_idx]
                    voronoi_finite_edges.append((center1, center2))
                    processed_pairs.add(pair)
            else:
                p1_idx = simplex[(j + 1) % 3]
                p2_idx = simplex[(j + 2) % 3]

                try:
                    p1 = tri.points[p1_idx]
                    p2 = tri.points[p2_idx]
                    p3 = tri.points[simplex[j]]
                except IndexError:
                     print(f"Ошибка индекса при поиске точек для бесконечного ребра симплекса {i}.")
                     continue

                start_point = circumcenters[i]
                edge_vec = p2 - p1
                perp_vec = np.array([-edge_vec[1], edge_vec[0]])

                norm = np.linalg.norm(perp_vec)
                if norm < EPSILON: continue
                perp_vec /= norm
                midpoint = (p1 + p2) / 2.0
                vec_mid_to_p3 = p3 - midpoint

                if np.dot(perp_vec, vec_mid_to_p3) < 0:
                    direction_vector = perp_vec
                else:
                    direction_vector = -perp_vec

                voronoi_infinite_rays.append((start_point, direction_vector))

    return voronoi_finite_edges, voronoi_infinite_rays, circumcenters


class VoronoiDelaunayApp:

    def __init__(self, master):
        self.master = master
        self.master.title("Делоне и Вороной")
        self.master.geometry("800x650")

        self.points = []
        self.mode = 'points'
        self.current_triangulation = None

        self.control_frame = tk.Frame(master)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.plot_frame = tk.Frame(master)
        self.plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.btn_delaunay = tk.Button(self.control_frame, text="Триангуляция Делоне", command=self.show_delaunay)
        self.btn_delaunay.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_voronoi = tk.Button(self.control_frame, text="Диаграмма Вороного", command=self.show_voronoi)
        self.btn_voronoi.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_clear = tk.Button(self.control_frame, text="Очистить", command=self.clear_all)
        self.btn_clear.pack(side=tk.LEFT, padx=5, pady=5)

        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect('equal', adjustable='box')
        self.ax.set_title("Кликните для добавления точек")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.fig.canvas.mpl_connect('button_press_event', self.add_point)
        self.plot_data()

    def add_point(self, event):
        if self.toolbar.mode or event.button != 1: return
        if event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            is_duplicate = False
            for px, py in self.points:
                if abs(px - x) < EPSILON * 10 and abs(py - y) < EPSILON * 10:
                    is_duplicate = True
                    break
            if not is_duplicate:
                self.points.append((x, y))
                self.mode = 'points'
                self.current_triangulation = None
                self.plot_data()
            else:
                print("Предупреждение: Точка слишком близко к существующей, проигнорирована.")


    def plot_data(self):
        self.ax.clear()
        points_array = np.array(self.points)
        title = "Кликните для добавления точек"
        if self.mode == 'delaunay': title = "Триангуляция Делоне"
        elif self.mode == 'voronoi': title = "Диаграмма Вороного"
        self.ax.set_title(title)

        if len(self.points) > 0:
            self.ax.plot(points_array[:, 0], points_array[:, 1], 'o', markersize=5, color='blue', label='Точки')
        else:
            self.ax.set_xlim(0, 1); self.ax.set_ylim(0, 1)
            self.ax.set_aspect('equal', adjustable='box')
            self.canvas.draw(); return

        if self.mode in ['delaunay', 'voronoi'] and self.current_triangulation is None and len(self.points) >= 3:
            print(f"Вызов custom_delaunay для режима '{self.mode}'...")
            self.current_triangulation = custom_delaunay(points_array)
            if self.current_triangulation is None:
                 messagebox.showerror("Ошибка", "Не удалось построить триангуляцию Делоне.")
                 self.mode = 'points'
                 self.ax.plot(points_array[:, 0], points_array[:, 1], 'o', markersize=5, color='red') # Показать точки красным
                 self.ax.set_title("Ошибка построения триангуляции")

            else:
                 print(f"custom_delaunay завершен. Симплексов: {len(self.current_triangulation.simplices)}")


        if self.mode == 'delaunay':
            if self.current_triangulation and hasattr(self.current_triangulation, 'simplices') and len(self.current_triangulation.simplices) > 0 :
                try:
                    self.ax.triplot(self.current_triangulation.points[:, 0],
                                    self.current_triangulation.points[:, 1],
                                    self.current_triangulation.simplices, color='black', linewidth=0.7)
                except Exception as e:
                     messagebox.showerror("Ошибка отрисовки триангуляции", f"Не удалось отрисовать:\n{e}")
                     self.mode = 'points'

        elif self.mode == 'voronoi':
            if self.current_triangulation:
                print("Вызов construct_voronoi_from_delaunay...")
                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()
                plot_bounds = {'xlim': xlim, 'ylim': ylim}

                voronoi_finite_edges, voronoi_infinite_rays, voronoi_vertices_map = \
                    construct_voronoi_from_delaunay(self.current_triangulation, plot_bounds)
                print(f"construct_voronoi_from_delaunay завершен. Ребер: {len(voronoi_finite_edges)}, Лучей: {len(voronoi_infinite_rays)}")


                for edge in voronoi_finite_edges:
                    p1, p2 = edge
                    self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='orange', linewidth=1)

                diag_length = np.sqrt((xlim[1] - xlim[0])**2 + (ylim[1] - ylim[0])**2)
                ray_length = diag_length * 1.5

                for start_point, direction in voronoi_infinite_rays:
                    norm = np.linalg.norm(direction)
                    if norm < EPSILON: continue
                    unit_direction = direction / norm
                    end_point = start_point + unit_direction * ray_length
                    self.ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]],
                                 color='orange', linestyle='--', linewidth=1)

                voronoi_verts = np.array(list(voronoi_vertices_map.values()))
                if len(voronoi_verts) > 0:
                    self.ax.plot(voronoi_verts[:, 0], voronoi_verts[:, 1], 's', markersize=3, color='green', label='Вершины Вороного')

                self.ax.plot(points_array[:, 0], points_array[:, 1], 'o', markersize=5, color='blue')

            elif len(self.points) >= 3:
                 messagebox.showwarning("Диаграмма Вороного", "Не удалось построить триангуляцию Делоне для Вороного.")
                 self.mode = 'points'

        if len(self.points) > 0:
            current_xlim = self.ax.get_xlim()
            current_ylim = self.ax.get_ylim()
            if abs(current_xlim[0] - 0) < EPSILON and abs(current_xlim[1] - 1) < EPSILON:
                 reset_limits = True
            else:
                 reset_limits = False


            min_coords = points_array.min(axis=0)
            max_coords = points_array.max(axis=0)
            range_coords = max_coords - min_coords
            margin_x = range_coords[0] * 0.1 + 0.1
            margin_y = range_coords[1] * 0.1 + 0.1
            new_xlim = (min_coords[0] - margin_x, max_coords[0] + margin_x)
            new_ylim = (min_coords[1] - margin_y, max_coords[1] + margin_y)

            if reset_limits or self.mode != 'voronoi':
                 self.ax.set_xlim(new_xlim)
                 self.ax.set_ylim(new_ylim)
            else:
                 self.ax.set_xlim(current_xlim)
                 self.ax.set_ylim(current_ylim)

        else:
            self.ax.set_xlim(0, 1); self.ax.set_ylim(0, 1)

        self.ax.set_aspect('equal', adjustable='box')
        self.canvas.draw()

    def show_delaunay(self):
        if len(self.points) < 3:
            messagebox.showwarning("Внимание", "Для триангуляции Делоне необходимо минимум 3 точки.")
            return
        self.mode = 'delaunay'
        self.current_triangulation = None
        self.plot_data()

    def show_voronoi(self):
        if len(self.points) < 3:
             messagebox.showwarning("Внимание", "Для построения диаграммы Вороного из триангуляции Делоне необходимо минимум 3 точки.")
             return
        self.mode = 'voronoi'
        self.plot_data()

    def clear_all(self):
        self.points = []
        self.mode = 'points'
        self.current_triangulation = None
        self.plot_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = VoronoiDelaunayApp(root)
    root.mainloop()
