import numpy as np
from stl import mesh
import math
import matplotlib.pyplot as plt
import json

# Cargar archivo STL
your_mesh = mesh.Mesh.from_file("frame_200_30.stl")

# Extraer todos los vértices
all_vertices = your_mesh.vectors.reshape(-1, 3)

# Filtrar vértices que están en la base (z ≈ 0)
base_vertices = [v for v in all_vertices if abs(v[2]) < 1e-4]

# Comprobar
if len(base_vertices) < 3:
    raise ValueError("No se encontraron suficientes vértices en la base (z=0)")

# Calcular centroide como centro aproximado
base_vertices_np = np.array(base_vertices)
center = base_vertices_np[:, :2].mean(axis=0)

# Calcular radio promedio
distances = np.linalg.norm(base_vertices_np[:, :2] - center, axis=1)
radius = distances.mean()

# Generar puntos cada 1.8 grados (200 puntos en total)
circle_points = []
for i in range(200):
    angle_rad = math.radians(i * 1.8)
    x = center[0] + radius * math.cos(angle_rad)
    y = center[1] + radius * math.sin(angle_rad)
    circle_points.append((x, y))

# Convertir a numpy para graficar
circle_points_np = np.array(circle_points)

# Crear diccionario indexado
circle_points_dict = {i: {"x": float(pt[0]), "y": float(pt[1])} for i, pt in enumerate(circle_points_np)}

# Guardar en un archivo JSON
with open("frame_coords.json", "w") as f:
    json.dump(circle_points_dict, f, indent=2)

print("Puntos guardados en 'puntos_circulo.json'")

# Graficar con matplotlib
plt.figure(figsize=(8, 8))
plt.scatter(base_vertices_np[:, 0], base_vertices_np[:, 1], c='lightgray', label='Vértices base (z≈0)', s=5)
plt.scatter(circle_points_np[:, 0], circle_points_np[:, 1], c='red', label='Puntos generados (cada 1.8°)', s=10)
plt.scatter(center[0], center[1], c='blue', label='Centro estimado', marker='x')
plt.axis('equal')
plt.legend()
plt.title("Puntos generados cada 1.8° sobre el anillo base")
plt.grid(True)
plt.show()
