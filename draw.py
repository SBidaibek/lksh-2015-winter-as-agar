from math import sqrt


def draw_players(c, pos, ps):
    # c - Canvas, pos - (x0, y0), ps - players
    x0, y0 = pos
    w = c.winfo_width()
    h = c.winfo_height()
    for p in ps:
        for b in p['balls']:
            lx = b['x'] - x0
            ly = b['y'] - y0
            r = sqrt(b['m'])
            c.create_oval(lx - r,
                          ly - r,
                          lx + r,
                          ly + r,
                          fill = p['color'])
            c.create_text(lx, ly, font='Times New Roman', text=p['name'])
    return c
