import tkinter as tk
import numpy as np
import math

class Object3D:
    def __init__(self):
        self.vertices = np.array([])
        self.edges = []

    def load_from_file(self, filename):
        verts = []
        edges = []
        with open(filename, "r") as f:
            for line in f:
                parts = line.strip().split()
                if not parts:
                    continue
                if parts[0] == "v" and len(parts) >= 4:
                    x, y, z = map(float, parts[1:4])
                    verts.append([x, y, z, 1.0])
                elif parts[0] == "e" and len(parts) >= 3:
                    i, j = map(int, parts[1:3])
                    edges.append((i, j))
        if verts:
            self.vertices = np.array(verts)
        else:
            self.vertices = np.array([])
        self.edges = edges

    def transform(self, matrix):
        if self.vertices.size == 0:
            return
        self.vertices = (matrix @ self.vertices.T).T

    def get_projected_vertices(self, d=300):
        projected = []
        for v in self.vertices:
            x, y, z, w = v
            factor = d / (z + d) if (z + d) != 0 else 1
            xp = x * factor
            yp = y * factor
            projected.append((xp, yp))
        return projected



def translation_matrix(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0, 1]
    ])

def scaling_matrix(sx, sy, sz):
    return np.array([
        [sx, 0,  0, 0],
        [0, sy,  0, 0],
        [0,  0, sz, 0],
        [0,  0,  0, 1]
    ])

def rotation_matrix_x(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [1, 0,  0, 0],
        [0, c, -s, 0],
        [0, s,  c, 0],
        [0, 0,  0, 1]
    ])

def rotation_matrix_y(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [ c, 0, s, 0],
        [ 0, 1, 0, 0],
        [-s, 0, c, 0],
        [ 0, 0, 0, 1]
    ])

def rotation_matrix_z(angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return np.array([
        [c, -s, 0, 0],
        [s,  c, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ])

class Editor3D:
    def __init__(self, master, object_file=None):
        self.master = master
        self.canvas = tk.Canvas(master, width=600, height=600, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.obj = Object3D()
        if object_file:
            self.obj.load_from_file(object_file)
        self.d = 300
        self.bind_keys()
        self.draw()

    def bind_keys(self):
        """
        q и e – масштабирование
        w и s – поворот вокруг X
        a и d – поворот вокруг Y
        z и x – поворот вокруг Z
        """
        self.master.bind("<Left>", lambda event: self.translate(-10, 0, 0))
        self.master.bind("<Right>", lambda event: self.translate(10, 0, 0))
        self.master.bind("<Up>", lambda event: self.translate(0, -10, 0))
        self.master.bind("<Down>", lambda event: self.translate(0, 10, 0))
        self.master.bind("q", lambda event: self.scale(1.1, 1.1, 1.1))
        self.master.bind("e", lambda event: self.scale(0.9, 0.9, 0.9))
        self.master.bind("w", lambda event: self.rotate_x(math.radians(-10)))
        self.master.bind("s", lambda event: self.rotate_x(math.radians(10)))
        self.master.bind("a", lambda event: self.rotate_y(math.radians(-10)))
        self.master.bind("d", lambda event: self.rotate_y(math.radians(10)))
        self.master.bind("z", lambda event: self.rotate_z(math.radians(-10)))
        self.master.bind("x", lambda event: self.rotate_z(math.radians(10)))
        self.master.bind("p", lambda event: self.draw())

    def translate(self, tx, ty, tz):
        T = translation_matrix(tx, ty, tz)
        self.obj.transform(T)
        self.draw()

    def scale(self, sx, sy, sz):
        S = scaling_matrix(sx, sy, sz)
        self.obj.transform(S)
        self.draw()

    def rotate_x(self, angle):
        R = rotation_matrix_x(angle)
        self.obj.transform(R)
        self.draw()

    def rotate_y(self, angle):
        R = rotation_matrix_y(angle)
        self.obj.transform(R)
        self.draw()

    def rotate_z(self, angle):
        R = rotation_matrix_z(angle)
        self.obj.transform(R)
        self.draw()

    def draw(self):
        self.canvas.delete("all")
        pts = self.obj.get_projected_vertices(self.d)
        w = self.canvas.winfo_width() / 2
        h = self.canvas.winfo_height() / 2
        pts_centered = [(x + w, y + h) for (x, y) in pts]
        for edge in self.obj.edges:
            i, j = edge
            if i < len(pts_centered) and j < len(pts_centered):
                x0, y0 = pts_centered[i]
                x1, y1 = pts_centered[j]
                self.canvas.create_line(x0, y0, x1, y1, fill="black")

def main():
    root = tk.Tk()
    root.title("3D Редактор")
    editor = Editor3D(root, object_file="object.txt")
    root.mainloop()

if __name__ == "__main__":
    main()
