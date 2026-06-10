import math
import os
import struct
import zlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
OUTPUT_PATH = os.path.join(ASSETS_DIR, 'icon.ico')


def clamp(value, minimum=0, maximum=255):
    return max(minimum, min(maximum, value))


def lerp(a, b, t):
    return a + (b - a) * t


def pack_png(width, height, rgba_bytes):
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        start = y * stride
        raw.extend(rgba_bytes[start:start + stride])

    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(bytes(raw), 9)) + chunk(b'IEND', b'')


def draw_icon(size):
    pixels = bytearray(size * size * 4)
    cx = cy = (size - 1) / 2.0
    radius = size * 0.5

    for y in range(size):
        for x in range(size):
            nx = x / (size - 1)
            ny = y / (size - 1)
            blend = (nx * 0.45) + (ny * 0.55)
            r = int(lerp(8, 21, blend))
            g = int(lerp(28, 152, blend))
            b = int(lerp(58, 173, blend))
            a = 255

            dx = (x - cx) / radius
            dy = (y - cy) / radius
            dist = math.sqrt(dx * dx + dy * dy)
            vignette = clamp(int((1.0 - max(0.0, dist)) * 18))
            r = clamp(r + vignette)
            g = clamp(g + vignette)
            b = clamp(b + vignette)

            # Soft ring behind the mark.
            ring_dx = x - cx
            ring_dy = y - (size * 0.47)
            ring_dist = math.sqrt(ring_dx * ring_dx + ring_dy * ring_dy)
            ring_outer = size * 0.19
            ring_inner = size * 0.12
            if ring_inner < ring_dist < ring_outer:
                r, g, b = 245, 247, 250
            elif ring_dist <= ring_inner:
                r, g, b = 255, 184, 77

            # Map-pin shape.
            pin_cx = cx
            pin_cy = size * 0.42
            head_dist = math.sqrt((x - pin_cx) ** 2 + (y - pin_cy) ** 2)
            head_radius = size * 0.18
            if head_dist <= head_radius:
                r, g, b = 246, 248, 252
            elif y > pin_cy and y < size * 0.80:
                tail_norm = (y - pin_cy) / (size * 0.38)
                tail_width = (1.0 - tail_norm) * size * 0.16
                if abs(x - pin_cx) <= tail_width * (0.72 + tail_norm * 0.30):
                    r, g, b = 246, 248, 252

            # Inner cutout for contrast.
            hole_dx = x - pin_cx
            hole_dy = y - pin_cy
            hole_dist = math.sqrt(hole_dx * hole_dx + hole_dy * hole_dy)
            if hole_dist <= size * 0.08:
                r, g, b = 15, 40, 76

            # Small briefcase mark at the bottom.
            case_left = int(size * 0.33)
            case_right = int(size * 0.67)
            case_top = int(size * 0.70)
            case_bottom = int(size * 0.80)
            handle_top = int(size * 0.64)
            handle_bottom = int(size * 0.69)
            if case_left <= x <= case_right and case_top <= y <= case_bottom:
                r, g, b = 255, 193, 92
            if int(size * 0.42) <= x <= int(size * 0.58) and handle_top <= y <= handle_bottom:
                r, g, b = 255, 193, 92

            idx = (y * size + x) * 4
            pixels[idx:idx + 4] = bytes((r, g, b, a))

    return bytes(pixels)


def build_ico():
    os.makedirs(ASSETS_DIR, exist_ok=True)
    sizes = [16, 32, 48, 64, 128, 256]
    images = []
    for size in sizes:
        rgba = draw_icon(size)
        images.append((size, pack_png(size, size, rgba)))

    header = struct.pack('<HHH', 0, 1, len(images))
    entry_size = 16
    offset = 6 + entry_size * len(images)
    entries = []
    payload = bytearray()

    for size, png_data in images:
        width = size if size < 256 else 0
        height = size if size < 256 else 0
        entries.append(struct.pack('<BBBBHHII', width, height, 0, 0, 1, 32, len(png_data), offset))
        payload.extend(png_data)
        offset += len(png_data)

    with open(OUTPUT_PATH, 'wb') as handle:
        handle.write(header)
        for entry in entries:
            handle.write(entry)
        handle.write(payload)


if __name__ == '__main__':
    build_ico()
    print(OUTPUT_PATH)
