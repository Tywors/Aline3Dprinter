import struct
import sys

def ascii_to_binary_stl(input_txt, output_stl):
    with open(input_txt, 'r') as f:
        lines = f.readlines()

    triangles = []
    current_normal = None
    current_vertices = []

    for line in lines:
        tokens = line.strip().split()
        if not tokens:
            continue

        if tokens[0] == 'facet' and tokens[1] == 'normal':
            current_normal = tuple(map(float, tokens[2:5]))
        elif tokens[0] == 'vertex':
            vertex = tuple(map(float, tokens[1:4]))
            current_vertices.append(vertex)
        elif tokens[0] == 'endfacet':
            if current_normal and len(current_vertices) == 3:
                triangles.append((current_normal, current_vertices[:3]))
            current_vertices = []

    with open(output_stl, 'wb') as f:
        f.write(b'Converted from ASCII STL' + b'\0' * (80 - len('Converted from ASCII STL')))
        f.write(struct.pack('<I', len(triangles)))

        for normal, vertices in triangles:
            f.write(struct.pack('<3f', *normal))
            for vertex in vertices:
                f.write(struct.pack('<3f', *vertex))
            f.write(struct.pack('<H', 0))  # Attribute byte count

    print(f"✅ Se ha creado el archivo binario STL: {output_stl} con {len(triangles)} triángulos.")

# Uso desde línea de comandos o pasando argumentos:
# ascii_to_binary_stl('entrada.txt', 'salida.stl')
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python ascii_to_binary_stl.py entrada.txt salida.stl")
    else:
        ascii_to_binary_stl(sys.argv[1], sys.argv[2])
