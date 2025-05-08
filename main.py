import math
import json
import argparse

def get_frame_coordinates(index, data_frame):
    # Convert index to string (since the keys are strings in the JSON)
    key = str(index)
    # Get coordinates if they exist
    if key in data_frame:
        return data_frame[key]['x'], data_frame[key]['y']
    else:
        return None

def generate_thin_rectangle(p1, p2, width, height, z_base):
    x1, y1 = p1['x'], p1['y']
    x2, y2 = p2['x'], p2['y']
    
    # Cálculo del vector dirección y su perpendicular
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    
    # Vectores unitarios
    if length > 0:
        ux, uy = dx / length, dy / length
        perp_x, perp_y = -uy, ux  # Vector perpendicular
    else:
        # Evitar división por cero si los puntos son idénticos
        ux, uy = 0, 0
        perp_x, perp_y = 1, 0
    
    # Crear los vértices del rectángulo con la altura z_base
    offset_x = (perp_x * width) / 2
    offset_y = (perp_y * width) / 2
    
    # Puntos base (inferior)
    a = (x1 - offset_x, y1 - offset_y, z_base)
    b = (x1 + offset_x, y1 + offset_y, z_base)
    c = (x2 + offset_x, y2 + offset_y, z_base)
    d = (x2 - offset_x, y2 - offset_y, z_base)
    
    # Puntos superiores
    a1 = (a[0], a[1], z_base + height)
    b1 = (b[0], b[1], z_base + height)
    c1 = (c[0], c[1], z_base + height)
    d1 = (d[0], d[1], z_base + height)
    
    # Definir las caras del rectángulo como triángulos
    triangles = [
        # Caras laterales
        (a, b, b1), (a, b1, a1),  # Cara 1
        (b, c, c1), (b, c1, b1),  # Cara 2
        (c, d, d1), (c, d1, c1),  # Cara 3
        (d, a, a1), (d, a1, d1),  # Cara 4
        
        # Cara superior e inferior
        (a1, b1, c1), (a1, c1, d1),  # Superior
        (a, d, c), (a, c, b),       # Inferior
    ]
    
    return triangles

def extract_facets_from_stl(stl_path):
    with open(stl_path, "r") as f:
        lines = f.readlines()

    # Find where the actual facets begin and end
    start = 0
    end = len(lines)
    
    # Skip 'solid' line
    if lines[0].strip().lower().startswith("solid"):
        start = 1
    # Skip 'endsolid' line
    if lines[-1].strip().lower().startswith("endsolid"):
        end -= 1

    return lines[start:end]

def generate_stl_from_segments(segments, point_to_layer, width, height, filename, layer_spacing):
    all_triangles = []
    
    for i, (p1, p2, point_index) in enumerate(segments):
        # Usar el índice del punto de origen para determinar la capa
        layer = point_to_layer.get(point_index, 0)
        z_base = layer * layer_spacing
        
        # Generar el rectángulo para este segmento en la capa correspondiente
        triangles = generate_thin_rectangle(p1, p2, width, height, z_base)
        all_triangles.extend(triangles)
    
    # Escribir el archivo STL
    with open(filename, "w") as f:
        f.write("solid hilos\n")
        for v1, v2, v3 in all_triangles:
            # Calcular la normal del triángulo (simplificado)
            f.write("  facet normal 0.0 0.0 0.0\n")
            f.write("    outer loop\n")
            for vx, vy, vz in (v1, v2, v3):
                f.write(f"      vertex {vx:.8f} {vy:.8f} {vz:.8f}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")
        #additional_facets = extract_facets_from_stl("marco_200_30.txt")
        #f.writelines(additional_facets)
        f.write("endsolid hilos\n")

# Programa principal
def main():
    parser = argparse.ArgumentParser(description="Generate LinesArt3D")
    parser.add_argument("--alinedeco", type=str, default="", help="File of alinedeco")
    parser.add_argument("--circle", type=str, default="", help="Coords circle")
    args = parser.parse_args()

    # Cargar el JSON con los puntos del círculo
    with open(args.circle, 'r') as f:
        data_frame = json.load(f)
    
    # Crear un mapeo de punto a capa
    # Cada punto del círculo tendrá su propia capa
    point_to_layer = {}
    unique_points = set()
    
    # Primera pasada: identificar todos los puntos únicos
    with open(args.alinedeco, 'r') as f:
        line = f.readline().strip()
        numbers = list(map(int, line.split(',')))
        
        for number in numbers:
            unique_points.add(number)
    
    # Asignar una capa a cada punto único
    for layer, point in enumerate(unique_points):
        point_to_layer[point] = layer
    
    print(f"Total de capas necesarias: {len(unique_points)}")
    
    # Procesar los segmentos
    segments = []
    with open(args.alinedeco, 'r') as f:
        line = f.readline().strip()
        numbers = list(map(int, line.split(',')))
        
        for i, number in enumerate(numbers):
            # Verificar si es el último punto
            if i == len(numbers) - 1:
                break
            else:
                # Obtener coordenadas del punto actual
                x1, y1 = get_frame_coordinates(number, data_frame)
                p1 = {"x": x1, "y": y1}
                
                # Obtener coordenadas del siguiente punto
                x2, y2 = get_frame_coordinates(numbers[i + 1], data_frame)
                p2 = {"x": x2, "y": y2}
                
                # Guardar el segmento con el índice del punto de origen para determinar la capa
                segments.append((p1, p2, number))
    
    # Generar el archivo STL
    generate_stl_from_segments(
        segments, 
        point_to_layer,
        width=0.126, 
        height=0.126, 
        filename="output.stl",
        layer_spacing=0.12
    )
    
    print(f"Archivo STL generado con {len(segments)} segmentos en {len(unique_points)} capas")

if __name__ == "__main__":
    main()