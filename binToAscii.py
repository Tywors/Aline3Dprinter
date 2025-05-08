import sys
import struct

def bin_to_ascii_stl(input_file, output_file):
    with open(input_file, 'rb') as f:
        header = f.read(80)
        num_triangles = struct.unpack('<I', f.read(4))[0]

        with open(output_file, 'w') as out:
            out.write("solid model\n")

            for _ in range(num_triangles):
                normal = struct.unpack('<3f', f.read(12))
                v1 = struct.unpack('<3f', f.read(12))
                v2 = struct.unpack('<3f', f.read(12))
                v3 = struct.unpack('<3f', f.read(12))
                attr_byte_count = f.read(2)

                out.write(f"  facet normal {normal[0]} {normal[1]} {normal[2]}\n")
                out.write("    outer loop\n")
                out.write(f"      vertex {v1[0]} {v1[1]} {v1[2]}\n")
                out.write(f"      vertex {v2[0]} {v2[1]} {v2[2]}\n")
                out.write(f"      vertex {v3[0]} {v3[1]} {v3[2]}\n")
                out.write("    endloop\n")
                out.write("  endfacet\n")

            out.write("endsolid model\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script.py archivo_entrada.stl archivo_salida.txt")
        sys.exit(1)

    bin_to_ascii_stl(sys.argv[1], sys.argv[2])
