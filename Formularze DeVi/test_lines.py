import fitz

def get_h_v_lines(page):
    paths = page.get_drawings()
    h_lines = []
    v_lines = []
    
    for path in paths:
        for item in path["items"]:
            if item[0] == "l":
                p1, p2 = item[1], item[2]
                # Horizontal line
                if abs(p1.y - p2.y) < 2:
                    h_lines.append({
                        "y": (p1.y + p2.y) / 2,
                        "x0": min(p1.x, p2.x),
                        "x1": max(p1.x, p2.x)
                    })
                # Vertical line
                elif abs(p1.x - p2.x) < 2:
                    v_lines.append({
                        "x": (p1.x + p2.x) / 2,
                        "y0": min(p1.y, p2.y),
                        "y1": max(p1.y, p2.y)
                    })
            elif item[0] == "re":
                r = item[1]
                # Add rect as 4 lines
                h_lines.append({"y": r.y0, "x0": r.x0, "x1": r.x1})
                h_lines.append({"y": r.y1, "x0": r.x0, "x1": r.x1})
                v_lines.append({"x": r.x0, "y0": r.y0, "y1": r.y1})
                v_lines.append({"x": r.x1, "y0": r.y0, "y1": r.y1})
    return h_lines, v_lines

def find_cell(px0, py0, px1, py1, h_lines, v_lines):
    pmx = (px0 + px1) / 2
    pmy = (py0 + py1) / 2
    
    # Find closest H line above
    top_line_y = 0
    for l in h_lines:
        if l["x0"] - 5 <= pmx <= l["x1"] + 5 and l["y"] <= py0 + 2:
            if l["y"] > top_line_y:
                top_line_y = l["y"]
                
    # Find closest H line below
    bottom_line_y = 10000
    for l in h_lines:
        if l["x0"] - 5 <= pmx <= l["x1"] + 5 and l["y"] >= py1 - 2:
            if l["y"] < bottom_line_y:
                bottom_line_y = l["y"]
                
    # Find closest V line left
    left_line_x = 0
    for l in v_lines:
        if l["y0"] - 5 <= pmy <= l["y1"] + 5 and l["x"] <= px0 + 2:
            if l["x"] > left_line_x:
                left_line_x = l["x"]
                
    # Find closest V line right
    right_line_x = 10000
    for l in v_lines:
        if l["y0"] - 5 <= pmy <= l["y1"] + 5 and l["x"] >= px1 - 2:
            if l["x"] < right_line_x:
                right_line_x = l["x"]
                
    return left_line_x, top_line_y, right_line_x, bottom_line_y

doc = fitz.open("/home/walkman/Документи/nip8.pdf")
page = doc[0]
h_lines, v_lines = get_h_v_lines(page)
print(f"H lines: {len(h_lines)}, V lines: {len(v_lines)}")

# Let's test with a fake phrase in the middle
# Say, roughly where "11. Numer" might be
print(find_cell(200, 100, 250, 110, h_lines, v_lines))
