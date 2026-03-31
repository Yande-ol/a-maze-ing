def to_hex(grid):
    hex_rows = []
    for row in grid:
        hex_string = "".join(f"{cell:x}" for cell in row)
        hex_rows.append(hex_string)
    return hex_rows
