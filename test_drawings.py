import fitz
import sys

doc = fitz.open("/home/walkman/Документи/nip8.pdf")
page = doc[0]
paths = page.get_drawings()
rects = 0
lines = 0
others = 0

for p in paths:
    for item in p["items"]:
        if item[0] == "re":
            rects += 1
        elif item[0] == "l":
            lines += 1
        else:
            others += 1

print(f"Paths: {len(paths)}")
print(f"Rectangles: {rects}")
print(f"Lines: {lines}")
print(f"Others: {others}")

