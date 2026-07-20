import os
import io
import csv
import math
import zipfile
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# --- PYTHON MICRO STICK FONT ENGINE ---
STICK_FONT = {
    'A': '0F509F,2878', 'B': '0F0060936707,679A6F0F', 'C': '936020020C2E6E9B', 'D': '000F6F9B936000',
    'E': '90000F9F,0767', 'F': '90000F,0767', 'G': '936020020C2E6E9B9757', 'H': '000F,909F,0797',
    'I': '404F', 'J': '909C7E2E0C', 'K': '000F,9007,479F', 'L': '000F9F', 'M': '0F0055909F',
    'N': '0F009F90', 'O': '2070929C7E2E0C0220', 'P': '0F0060936707', 'Q': '2070929C7E2E0C0220,6A9F',
    'R': '0F0060936707,479F', 'S': '927020020628789A9C7E2E0C', 'T': '0090,404F', 'U': '000C2E7E9C90',
    'V': '004F90', 'W': '000F499F90', 'X': '009F,900F', 'Y': '0046,90464F', 'Z': '00900F9F',
    '0': '2070929C7E2E0C0220,0F90', '1': '22404F', '2': '02207092960F9F', '3': '02207092769A9C7E2E0C,2676',
    '4': '70080A9A,707F', '5': '90000676989C7E2E0C', '6': '927020020C2E7E9C987606', '7': '00904F',
    '8': '270502207092957727090C2E7E9C9977', '9': '0C2E7E9C92702002062898', 
    '-': '2878', '/': '0F90', '.': '4E4F5F5E4E', '#': '2484,2A8A,303F,707F', ' ': ''
}

def draw_text_paths(text, x_center, y_center, font_size, max_line_width, arc_type, text_radius):
    path_string = ""
    text = str(text).upper()
    char_w, char_h, char_sp = 10, 15, 4
    total_logical_w = len(text) * char_w + max(0, len(text) - 1) * char_sp
    if total_logical_w == 0: return ""
    
    scale = min(font_size / char_h, max_line_width / total_logical_w)
    
    for i, char in enumerate(text):
        strokes = STICK_FONT.get(char, '')
        char_center_x = (i * (char_w + char_sp)) + (char_w / 2) - (total_logical_w / 2)
        
        if strokes:
            for line in strokes.split(','):
                for j in range(0, len(line), 2):
                    lx, ly = int(line[j], 16), int(line[j+1], 16)
                    off_x, off_y = (lx - char_w/2) * scale, (ly - char_h/2) * scale
                    
                    if arc_type == 'none':
                        fx, fy = x_center + (char_center_x * scale) + off_x, y_center + off_y
                    elif arc_type == 'top':
                        angle = -math.pi/2 + ((char_center_x * scale + off_x) / text_radius)
                        r = text_radius - off_y
                        fx, fy = x_center + r * math.cos(angle), y_center + r * math.sin(angle)
                    elif arc_type == 'bottom':
                        angle = math.pi/2 - ((char_center_x * scale + off_x) / text_radius)
                        r = text_radius + off_y
                        fx, fy = x_center + r * math.cos(angle), y_center + r * math.sin(angle)
                        
                    path_string += f" M {fx:.3f} {fy:.3f}" if j == 0 else f" L {fx:.3f} {fy:.3f}"
    return path_string

def generate_svg_plate(shape, dim1, dim2, lines):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {dim1+4} {dim1+4 if shape=="torus" else dim2+4}">'
    if shape == 'rectangle':
        max_lines, max_h, max_w = 5, (dim2 * 0.9) / 5, dim1 * 0.9
        for i, text in enumerate(lines[:5]):
            if text:
                y_pos = (dim2 * 0.05) + (max_h * i) + (max_h / 2)
                paths = draw_text_paths(text, dim1/2, y_pos, max_h * 0.8, max_w, 'none', 0)
                svg += f'<path d="{paths}" fill="none" stroke="#000" stroke-width="0.5" stroke-linecap="round" />'
    elif shape == 'torus':
        cx, cy, text_rad = dim1/2, dim1/2, (dim1/2 + dim2/2)/2
        max_fh, max_arc = (dim1 - dim2)/2 * 0.7, (math.pi * text_rad) * 0.9
        if len(lines) > 0 and lines[0]:
            svg += f'<path d="{draw_text_paths(lines[0], cx, cy, max_fh, max_arc, "top", text_rad)}" fill="none" stroke="#000" stroke-width="0.5" stroke-linecap="round" />'
        if len(lines) > 1 and lines[1]:
            svg += f'<path d="{draw_text_paths(lines[1], cx, cy, max_fh, max_arc, "bottom", text_rad)}" fill="none" stroke="#000" stroke-width="0.5" stroke-linecap="round" />'
    svg += '</svg>'
    return svg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bulk', methods=['POST'])
def bulk_generate():
    if 'csv_file' not in request.files:
        return "No file uploaded", 400
        
    file = request.files['csv_file']
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Expected CSV Format: shape, dim1(width/od), dim2(height/id), line1, line2, line3, line4, line5
        # Example: torus, 35, 23, SN-001, BATCH 4
        next(csv_input, None) # Skip header row
        for i, row in enumerate(csv_input):
            if len(row) < 3: continue
            shape, dim1, dim2 = row[0].strip().lower(), float(row[1]), float(row[2])
            lines = [col.strip() for col in row[3:8]]
            
            svg_data = generate_svg_plate(shape, dim1, dim2, lines)
            filename = f"plate_{i+1}_{shape}_{lines[0]}.svg"
            zf.writestr(filename, svg_data)
            
    memory_file.seek(0)
    return send_file(memory_file, download_name="bulk_plates.zip", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
