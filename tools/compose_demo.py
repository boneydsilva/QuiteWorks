"""Cut a recording into the film the home page plays.

    python tools/compose_demo.py "%TEMP%\wq-demo\shoot"

Reads the frames record_demo.py left in that folder and writes
workqueue-demo.mp4 and demo-poster.jpg beside them. Needs Pillow and
imageio-ffmpeg (pip install pillow imageio-ffmpeg).


Every pixel of product on screen is real capture. What this adds is the things
a camera would do: framing, a slow push on the thing that matters, a caption
that says one idea at a time, and a dissolve between shots.

A shot names its source window in recording time and a camera - centre and
width, in CSS pixels of the dashboard (or physical pixels of the strip) - at
the start and at the end. The panel it plays inside stays fixed on the stage,
so the move happens inside the frame, the way a locked-off camera zooms.
"""
import glob, json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
    sys.exit(__doc__)
OUT = os.path.abspath(sys.argv[1])
W, H = 1920, 1080
FPS = 30
DASH_SCALE = 2                      # dashboard frames are 2x their CSS size
XF = 0.45                           # cross-dissolve, seconds

F_LIGHT = "C:/Windows/Fonts/segoeuil.ttf"
F_SEMI = "C:/Windows/Fonts/segoeuisl.ttf"
F_REG = "C:/Windows/Fonts/segoeui.ttf"
F_BOLD = "C:/Windows/Fonts/segoeuib.ttf"

INK = (233, 237, 243)
DIM = (125, 136, 152)
ACCENT = (239, 159, 87)

meta = json.load(open(os.path.join(OUT, "recording.json")))
T0 = meta["t0"]

def load(kind):
    fs = [(int(os.path.basename(p)[:-4]) / 1000.0 - T0, p)
          for p in glob.glob(os.path.join(OUT, "frames", kind, "*.jpg"))]
    return sorted(fs)

DASH = load("dash")
BAND = load("band")
print(f"source: {len(DASH)} dashboard frames, {len(BAND)} strip frames")

_cache = {}
def frame_at(kind, t):
    """The frame that was on screen at recording time t - the last one taken."""
    fs = DASH if kind == "dash" else BAND
    lo, hi = 0, len(fs) - 1
    if t <= fs[0][0]:
        pick = fs[0][1]
    else:
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if fs[mid][0] <= t: lo = mid
            else: hi = mid - 1
        pick = fs[lo][1]
    im = _cache.get(pick)
    if im is None:
        im = Image.open(pick).convert("RGB")
        _cache.clear()                      # consecutive frames reuse one file
        _cache[pick] = im
    return im

# --- the stage -------------------------------------------------------------

def backdrop():
    """A dark room with a soft pool of light behind the product."""
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)],
               fill=(int(20 - 9 * k), int(25 - 11 * k), int(33 - 15 * k)))
    glow = Image.new("L", (W // 4, H // 4), 0)
    ImageDraw.Draw(glow).ellipse([-W // 16, H // 40, W // 4 + W // 16, H // 4 - H // 12],
                                 fill=74)
    glow = glow.filter(ImageFilter.GaussianBlur(46)).resize((W, H), Image.BILINEAR)
    return Image.composite(Image.new("RGB", (W, H), (52, 64, 86)), bg, glow)

BG = backdrop()

_shadow = {}
def shadow_for(w, h, radius):
    key = (w, h, radius)
    if key not in _shadow:
        pad = 90
        m = Image.new("L", (w + pad * 2, h + pad * 2), 0)
        ImageDraw.Draw(m).rounded_rectangle([pad, pad + 12, pad + w, pad + h + 26],
                                            radius=radius, fill=150)
        _shadow[key] = m.filter(ImageFilter.GaussianBlur(34))
    return _shadow[key]

_mask = {}
def mask_for(w, h, radius):
    key = (w, h, radius)
    if key not in _mask:
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=255)
        _mask[key] = m
    return _mask[key]

def ease(k):
    return k * k * (3 - 2 * k)

def lerp(a, b, k):
    return a + (b - a) * k

def draw_panel(canvas, kind, src_t, cam, rect, radius=14, scale=1.0):
    """Crop the camera's view out of the source frame and lay it on the stage."""
    x, y, w, h = rect
    im = frame_at(kind, src_t)
    px = DASH_SCALE if kind == "dash" else 1
    cx, cy, vw = cam
    vh = vw * h / w
    box = [(cx - vw / 2) * px, (cy - vh / 2) * px, (cx + vw / 2) * px, (cy + vh / 2) * px]
    box = [max(0, box[0]), max(0, box[1]), min(im.width, box[2]), min(im.height, box[3])]
    view = im.resize((w, h), Image.LANCZOS, box=box)

    pad = 90
    sh = shadow_for(w, h, radius)
    canvas.paste((0, 0, 0), (x - pad, y - pad), sh)
    canvas.paste(view, (x, y), mask_for(w, h, radius))
    edge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius,
                                           outline=(255, 255, 255, 34), width=1)
    canvas.paste(edge, (x, y), edge)
    return box, view.size

# --- type ------------------------------------------------------------------

_fonts = {}
def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]

def text_w(d, s, f, track=0):
    return sum(d.textlength(c, font=f) + track for c in s) - (track if s else 0)

def draw_tracked(d, xy, s, f, fill, track=0, anchor_mid=True):
    x, y = xy
    if anchor_mid:
        x -= text_w(d, s, f, track) / 2
    for c in s:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + track

def wrap(d, s, f, limit):
    words, lines, cur = s.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines

def draw_caption(canvas, text, alpha, y=946):
    if not text or alpha <= 0.01:
        return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = font(F_LIGHT, 44)
    lines = wrap(d, text, f, 1440)
    yy = y - (len(lines) - 1) * 27
    for line in lines:
        d.text((W / 2, yy), line, font=f, fill=INK + (int(255 * alpha),), anchor="ma")
        yy += 54
    canvas.paste(layer, (0, 0), layer)

def draw_label(canvas, text, x, y, alpha=1.0):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_tracked(d, (x, y), text.upper(), font(F_SEMI, 19),
                 DIM + (int(255 * alpha),), track=2.6, anchor_mid=False)
    canvas.paste(layer, (0, 0), layer)

# --- the pointer -----------------------------------------------------------

CURSOR = [(c["t"] - T0, c["x"], c["y"], c["click"]) for c in meta["cursor"]]

def cursor_at(t):
    if not CURSOR or t < CURSOR[0][0]:
        return None
    prev = CURSOR[0]
    for c in CURSOR:
        if c[0] > t:
            span = c[0] - prev[0]
            k = 0 if span <= 0 else min(1, (t - prev[0]) / span)
            return (lerp(prev[1], c[1], k), lerp(prev[2], c[2], k))
        prev = c
    return (prev[1], prev[2])

def click_strength(t):
    best = 0.0
    for ct, _, _, is_click in CURSOR:
        if is_click and 0 <= t - ct <= 0.45:
            best = max(best, 1 - (t - ct) / 0.45)
    return best

ARROW = [(0, 0), (0, 17.5), (4.2, 13.6), (7.1, 20), (10.1, 18.7), (7.3, 12.5), (12.4, 12.2)]

def draw_cursor(canvas, css_xy, box, rect, alpha=1.0, t=0.0):
    """Put the pointer where the pointer actually was, mapped into the frame."""
    if css_xy is None or alpha <= 0.01:
        return
    x, y, w, h = rect
    sx = (css_xy[0] * DASH_SCALE - box[0]) / max(1e-6, box[2] - box[0])
    sy = (css_xy[1] * DASH_SCALE - box[1]) / max(1e-6, box[3] - box[1])
    if not (-0.02 <= sx <= 1.02 and -0.02 <= sy <= 1.02):
        return
    px, py = x + sx * w, y + sy * h
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ring = click_strength(t)
    if ring > 0:
        r = 12 + 34 * (1 - ring)
        d.ellipse([px - r, py - r, px + r, py + r],
                  outline=(255, 255, 255, int(150 * ring)), width=3)
    k = 2.05
    pts = [(px + dx * k, py + dy * k) for dx, dy in ARROW]
    d.polygon(pts, fill=(255, 255, 255, int(255 * alpha)),
              outline=(12, 15, 20, int(220 * alpha)))
    canvas.paste(layer, (0, 0), layer)

# --- panels ----------------------------------------------------------------

P_WIDE = (120, 336, 1680, 420)      # 4.00 - the composer row, the history rows
P_BOARD = (150, 120, 1620, 790)     # 2.051 - the whole board
P_TALL = (400, 130, 1120, 700)      # 1.60 - the picker, which is taller than wide
P_BAND_FULL = (40, 150, 1840, 42)   # the strip where it lives: the top of a screen
P_BAND_ZOOM = (110, 470, 1700, 85)  # 20.0 - a crop 880 wide, all 44 rows of it
P_CARD_F = (330, 176, 1260, 504)    # 2.50
P_BAND_F = (330, 754, 1260, 71)     # 17.7 - a crop 780 wide
P_ROWS = (100, 330, 1720, 430)      # 4.00

DASH_LABEL = "the manager's dashboard"
BAND_LABEL = "asha's screen \u2014 the top 34 pixels of it"

# --- the shot list ---------------------------------------------------------
# film in/out, then what plays inside.

SHOTS = [
    dict(t=(0.0, 3.2), kind="title",
         title="WorkQueue",
         sub="Hand out work. Know how long it took."),

    dict(t=(3.2, 11.4), kind="dash", src=(3.5, 16.5), rect=P_WIDE, label=DASH_LABEL,
         cam=((690, 185, 1420), (630, 160, 1220)), cursor=True,
         caption="A manager types the job once."),

    dict(t=(11.4, 17.6), kind="dash", src=(24.0, 31.5), rect=P_TALL, label=DASH_LABEL,
         cam=((1500, 250, 800), (1560, 230, 660)), cursor=True,
         caption="and picks whose screen it goes to."),

    dict(t=(17.6, 23.4), kind="dash", src=(31.6, 38.5), rect=P_BOARD, label=DASH_LABEL,
         cam=((960, 468, 1920), (470, 350, 940)), cursor=True,
         caption="Assign. It is on the board before the mouse is back."),

    dict(t=(23.4, 26.8), kind="band", src=(40.0, 43.4), rect=P_BAND_FULL, label=BAND_LABEL,
         cam=((960, 22, 1920), (960, 22, 1920)), screen=True,
         caption="Every employee has a strip docked at the top of their screen. "
                 "That rectangle is the rest of it."),

    dict(t=(26.8, 32.4), kind="band", src=(43.2, 48.8), rect=P_BAND_ZOOM, label=BAND_LABEL,
         cam=((430, 22, 880), (430, 22, 880)),
         caption="Two seconds later the job is on it. No app to open, nothing to accept."),

    dict(t=(32.4, 39.6), kind="pair", src=(49.5, 60.5),
         rect=P_CARD_F, rect2=P_BAND_F,
         cam=((810, 235, 600), (810, 235, 560)), cam2=((390, 22, 780), (390, 22, 780)),
         label=DASH_LABEL, label2=BAND_LABEL,
         caption="The clock started itself the moment it arrived. Nobody has to remember to."),

    dict(t=(39.6, 43.2), kind="band", src=(63.6, 67.2), rect=P_BAND_ZOOM, label=BAND_LABEL,
         cam=((430, 22, 880), (430, 22, 880)),
         caption="She presses Complete once, and her strip goes quiet."),

    dict(t=(43.2, 48.6), kind="dash", src=(65.4, 70.8), rect=P_BOARD, label=DASH_LABEL,
         cam=((960, 468, 1920), (1600, 260, 640)),
         caption="The card crosses the board on its own."),

    dict(t=(48.6, 55.8), kind="dash", src=(78.4, 80.9), rect=P_BOARD, label=DASH_LABEL,
         cam=((960, 468, 1920), (760, 400, 1500)),
         caption="Two timestamps nobody typed. That is the whole of the reporting."),

    dict(t=(55.8, 62.0), kind="dash", src=(84.6, 87.6), rect=P_ROWS, label=DASH_LABEL,
         cam=((960, 468, 1900), (890, 500, 1760)),
         caption="Waited five seconds. Took twenty-four. Every task, exportable."),

    dict(t=(62.0, 67.0), kind="end",
         title="WorkQueue",
         sub="Runs on a PC you already own. Bought once, not rented.",
         url="boneydsilva.com"),
]

DURATION = SHOTS[-1]["t"][1]

# --- rendering one shot ----------------------------------------------------

def render(shot, t):
    canvas = BG.copy()
    t_in, t_out = shot["t"]
    k = 0 if t_out <= t_in else min(1, max(0, (t - t_in) / (t_out - t_in)))
    fade = min(1, (t - t_in) / 0.5, (t_out - t) / 0.5, 1)
    fade = max(0.0, fade)

    if shot["kind"] in ("title", "end"):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        a = int(255 * min(1, max(0, min((t - t_in) / 0.8, (t_out - t) / 0.8, 1))))
        base = 400 if shot["kind"] == "title" else 380
        d.text((W / 2, base), shot["title"], font=font(F_LIGHT, 122), fill=INK + (a,),
               anchor="ma")
        d.text((W / 2, base + 190), shot["sub"], font=font(F_LIGHT, 40),
               fill=DIM + (a,), anchor="ma")
        if shot.get("url"):
            draw_tracked(d, (W / 2, base + 300), shot["url"], font(F_SEMI, 26),
                         ACCENT + (a,), track=3.2)
        canvas.paste(layer, (0, 0), layer)
        return canvas

    if shot.get("screen"):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).rounded_rectangle(
            [30, 140, 1890, 898], radius=18,
            fill=(255, 255, 255, 7), outline=(255, 255, 255, 22), width=1)
        canvas.paste(layer, (0, 0), layer)

    e = ease(k)
    src = lerp(shot["src"][0], shot["src"][1], k)
    cam = tuple(lerp(a, b, e) for a, b in zip(*shot["cam"]))

    if shot["kind"] == "pair":
        box, _ = draw_panel(canvas, "dash", src, cam, shot["rect"])
        cam2 = tuple(lerp(a, b, e) for a, b in zip(*shot["cam2"]))
        draw_panel(canvas, "band", src, cam2, shot["rect2"], radius=8)
        draw_label(canvas, shot["label"], shot["rect"][0] + 4, shot["rect"][1] - 34, fade)
        draw_label(canvas, shot["label2"], shot["rect2"][0] + 4, shot["rect2"][1] - 34, fade)
    else:
        kind = "dash" if shot["kind"] == "dash" else "band"
        radius = 14 if kind == "dash" else 8
        box, _ = draw_panel(canvas, kind, src, cam, shot["rect"], radius=radius)
        draw_label(canvas, shot["label"], shot["rect"][0] + 4, shot["rect"][1] - 36, fade)
        if shot.get("cursor"):
            draw_cursor(canvas, cursor_at(src), box, shot["rect"], fade, src)

    draw_caption(canvas, shot["caption"], fade)
    return canvas

def shot_at(t):
    for s in SHOTS:
        if s["t"][0] <= t < s["t"][1]:
            return s
    return SHOTS[-1]

def compose(t):
    cur = shot_at(t)
    nxt = None
    for i, s in enumerate(SHOTS):
        if s is cur and i + 1 < len(SHOTS):
            nxt = SHOTS[i + 1]
    a = render(cur, t)
    if nxt and t > cur["t"][1] - XF:
        k = (t - (cur["t"][1] - XF)) / XF
        b = render(nxt, t)
        a = Image.blend(a, b, ease(min(1, max(0, k))))
    # Open on black, close on black.
    if t < 0.7:
        a = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), a, ease(t / 0.7))
    if t > DURATION - 0.9:
        a = Image.blend(a, Image.new("RGB", (W, H), (0, 0, 0)),
                        ease(min(1, (t - (DURATION - 0.9)) / 0.9)))
    return a

# --- go --------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "still":
        # Cheap way to check the framing of a shot without a four minute render.
        for t in [float(x) for x in sys.argv[3:]]:
            compose(t).save(os.path.join(OUT, f"still-{t:g}.png"))
            print("still-%g.png" % t)
        sys.exit()

    dest = os.path.join(OUT, "workqueue-demo.mp4")
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    proc = subprocess.Popen([
        ff, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-profile:v", "high",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", dest,
    ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total = int(DURATION * FPS)
    for i in range(total):
        proc.stdin.write(compose(i / FPS).tobytes())
        if i % 60 == 0:
            print(f"  {i/FPS:5.1f}s / {DURATION:.1f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", dest, os.path.getsize(dest) // 1024, "KB")

    # The poster carries a play button, so it does not carry a caption too.
    for shot in SHOTS:
        shot["caption"] = ""
    poster = os.path.join(OUT, "demo-poster.jpg")
    compose(36.0).resize((1600, 900), Image.LANCZOS).save(
        poster, quality=85, optimize=True, progressive=True)
    print("wrote", poster, os.path.getsize(poster) // 1024, "KB")
