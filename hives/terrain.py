"""Server-drawn terrain graphics for The Contour Hive design system. No API, no tiles, no images.

- contours(seed): topographic contour rings, a fingerprint unique to each hive (deterministic per slug)
- ridges(seed): layered mountain silhouettes for heroes and section edges
- arc_svg(regions): the Himalayan arc from Nanga Parbat to Namcha Barwa with a hex pin per hive
- profile_svg(profile): a journey's sleeping-altitude profile, with the 3,000 m acclimatisation line
"""
import hashlib
import math
import random
from functools import lru_cache

from django.utils.html import escape

from .atlas import _outlines

# Real summits along the Great Himalaya crest, west to east (lat, lng, metres)
PEAKS = [
    ("Nanga Parbat", 35.24, 74.59, 8126), ("Nun", 33.98, 76.02, 7135), ("Kamet", 30.92, 79.59, 7756),
    ("Nanda Devi", 30.37, 79.97, 7816), ("Dhaulagiri", 28.70, 83.49, 8167), ("Annapurna I", 28.60, 83.82, 8091),
    ("Manaslu", 28.55, 84.56, 8163), ("Everest", 27.99, 86.93, 8849), ("Kangchenjunga", 27.70, 88.15, 8586),
    ("Jomolhari", 27.83, 89.27, 7326), ("Gangkhar Puensum", 28.05, 90.45, 7570), ("Namcha Barwa", 29.63, 95.06, 7782),
]
LABEL_PEAKS = {"Nanga Parbat", "Nanda Devi", "Everest", "Kangchenjunga", "Namcha Barwa", "Dhaulagiri"}


def _rng(seed):
    return random.Random(int(hashlib.md5(seed.encode()).hexdigest()[:8], 16))


def _smooth_closed(pts):
    """Catmull-Rom → cubic Bézier through closed points."""
    n = len(pts)
    d = [f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(n):
        p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    return "".join(d) + "Z"


@lru_cache(maxsize=64)
def contours(seed, w=1200, h=700, peaks=3, levels=9):
    """Concentric wobbly rings around a few summits: reads as a topographic sheet."""
    rng = _rng("c" + seed)
    paths = []
    for k in range(peaks):
        cx, cy = rng.uniform(0.15, 0.85) * w, rng.uniform(0.2, 0.8) * h
        base = rng.uniform(0.22, 0.42) * min(w, h)
        harm = [(rng.randint(2, 6), rng.uniform(0.04, 0.13), rng.uniform(0, 6.28)) for _ in range(4)]
        for lv in range(levels):
            r0 = base * (1 - lv / (levels + 0.6))
            pts = []
            for i in range(28):
                t = i / 28 * 2 * math.pi
                f = 1 + sum(a * math.sin(m * t + ph + lv * 0.35) for m, a, ph in harm)
                pts.append((cx + math.cos(t) * r0 * f * 1.35, cy + math.sin(t) * r0 * f))
            paths.append((lv, _smooth_closed(pts)))
    out = [f'<svg class="topo" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">']
    for lv, d in paths:
        cls = "topo__idx" if lv % 4 == 0 else "topo__line"
        out.append(f'<path class="{cls}" d="{d}"/>')
    out.append("</svg>")
    return "".join(out)


@lru_cache(maxsize=64)
def ridges(seed, w=1600, h=420, layers=4):
    """Layered ridge silhouettes, far (pale) to near (dark). Each layer is a path with class ridge--N."""
    rng = _rng("r" + seed)
    out = [f'<svg class="ridges" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">']
    for L in range(layers):
        top = h * (0.12 + L * 0.17)
        amp = h * (0.30 - L * 0.05)
        n = 9 + L * 3
        xs = [i * w / n for i in range(n + 1)]
        pts = []
        for x in xs:
            y = top + rng.uniform(0, amp)
            pts.append((x, y))
        d = f"M0,{h} L0,{pts[0][1]:.1f} "
        for i in range(1, len(pts)):
            px, py = pts[i - 1]
            x, y = pts[i]
            mx = (px + x) / 2 + rng.uniform(-w / n / 6, w / n / 6)
            peak = min(py, y) - rng.uniform(0, amp * 0.55)
            d += f"L{mx:.1f},{peak:.1f} L{x:.1f},{y:.1f} "
        d += f"L{w},{h} Z"
        out.append(f'<path class="ridge ridge--{L}" d="{d}" data-depth="{L}"/>')
    out.append("</svg>")
    return "".join(out)


def _hex(cx, cy, r):
    return " ".join(f"{cx + r * math.cos(math.radians(60 * i)):.1f},{cy + r * math.sin(math.radians(60 * i)):.1f}" for i in range(6))


def arc_svg(regions):
    """The Himalayan arc, drawn from Natural Earth outlines with a hex pin for each hive."""
    W, H = 1400, 560
    lng0, lng1, lat0, lat1 = 72.4, 97.6, 25.6, 36.6
    k = math.cos(math.radians(31))
    sx = W / ((lng1 - lng0) * k)
    sy = H / (lat1 - lat0)

    def P(lng, lat):
        return (lng - lng0) * k * sx, (lat1 - lat) * sy

    def path(rings):
        parts = []
        for ring in rings:
            xs = [x for x, _ in ring]
            ys = [y for _, y in ring]
            if max(xs) < lng0 or min(xs) > lng1 or max(ys) < lat0 or min(ys) > lat1:
                continue
            parts.append("M" + "L".join("%.1f,%.1f" % P(x, y) for x, y in ring) + "Z")
        return "".join(parts)

    o = _outlines()
    s = [f'<svg class="arc__svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="arc-t" xmlns="http://www.w3.org/2000/svg">',
         '<title id="arc-t">The Himalayan arc from Kashmir to Arunachal, with the eleven hives we plan trips in</title>']
    for name, rings in o.get("countries", {}).items():
        d = path(rings)
        if d:
            home = name in ("India", "Nepal", "Bhutan")
            s.append(f'<path class="arc__land{"" if home else " arc__land--other"}" d="{d}"><title>{escape(name)}</title></path>')
    for name, rings in o.get("states", {}).items():
        d = path(rings)
        if d:
            s.append(f'<path class="arc__state" d="{d}"/>')
    crest = [P(lng, lat) for _, lat, lng, _ in PEAKS]
    s.append('<path class="arc__crest" d="M' + " ".join("%.1f,%.1f" % p for p in crest) + '"/>')
    for (name, lat, lng, m), (x, y) in zip(PEAKS, crest):
        s.append(f'<g class="arc__peak"><path d="M{x - 7:.1f},{y + 6:.1f} L{x:.1f},{y - 8:.1f} L{x + 7:.1f},{y + 6:.1f}Z"/>'
                 f'<title>{escape(name)} {m:,} m</title>')
        if name in LABEL_PEAKS:
            s.append(f'<text x="{x:.1f}" y="{y - 14:.1f}" text-anchor="middle">{escape(name)} · {m:,} m</text>')
        s.append("</g>")
    placed = []
    for r in regions:
        lat, lng = r.get("lat"), r.get("lng")
        if lat is None or lng is None:
            continue
        x, y = P(lng, lat)
        for px, py in placed:  # keep pins apart
            if math.hypot(x - px, y - py) < 58:
                y += 52 if y >= py else -52
        placed.append((x, y))
        s.append(f'<a class="arc__pin" href="{escape(r["url"])}" data-land="{r["slug"]}" data-hive="{r["slug"]}">'
                 f'<title>{escape(r["name"])}</title><polygon class="arc__hex" points="{_hex(x, y, 24)}"/>'
                 f'<text class="arc__name" x="{x:.1f}" y="{y + 44:.1f}" text-anchor="middle">{escape(r["name"])}</text></a>')
    s.append(f'<g class="arc__scale" transform="translate(28,{H - 26})">')
    km = 500
    bar = km / 111.2 * sy  # one degree of latitude ≈ 111.2 km
    s.append(f'<line x1="0" y1="0" x2="{bar:.1f}" y2="0"/><line x1="0" y1="-5" x2="0" y2="5"/><line x1="{bar:.1f}" y1="-5" x2="{bar:.1f}" y2="5"/>'
             f'<text x="{bar / 2:.1f}" y="-9" text-anchor="middle">{km} km</text></g>')
    s.append("</svg>")
    return "".join(s), [{"slug": r["slug"], "x": round(P(r["lng"], r["lat"])[0] / W * 100, 2),
                         "y": round(P(r["lng"], r["lat"])[1] / H * 100, 2)} for r in regions if r.get("lat") is not None]


def profile_svg(profile, title=""):
    """Sleeping altitude by night. profile = [{'day', 'alt', 'name'}]."""
    if len(profile) < 2:
        return ""
    W, H, L, R, T, B = 900, 300, 64, 24, 34, 54
    top = max(4000, math.ceil(max(p["alt"] for p in profile) / 1000) * 1000)
    n = len(profile)

    def X(i):
        return L + (W - L - R) * (i / (n - 1))

    def Y(a):
        return T + (H - T - B) * (1 - a / top)

    s = [f'<svg class="prof__svg" viewBox="0 0 {W} {H}" role="img" aria-label="Sleeping altitude by night{": " + escape(title) if title else ""}" xmlns="http://www.w3.org/2000/svg">']
    for a in range(0, top + 1, 1000):
        s.append(f'<line class="prof__grid" x1="{L}" x2="{W - R}" y1="{Y(a):.1f}" y2="{Y(a):.1f}"/>'
                 f'<text class="prof__axis" x="{L - 10}" y="{Y(a) + 4:.1f}" text-anchor="end">{a:,}</text>')
    s.append(f'<line class="prof__acc" x1="{L}" x2="{W - R}" y1="{Y(3000):.1f}" y2="{Y(3000):.1f}"/>'
             f'<text class="prof__acc-t" x="{W - R}" y="{Y(3000) - 7:.1f}" text-anchor="end">3,000 m: sleep higher slowly</text>')
    pts = [(X(i), Y(p["alt"])) for i, p in enumerate(profile)]
    area = f"M{pts[0][0]:.1f},{Y(0):.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts) + f" L{pts[-1][0]:.1f},{Y(0):.1f}Z"
    s.append(f'<path class="prof__area" d="{area}"/>')
    s.append('<polyline class="prof__line" points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '"/>')
    step = max(1, math.ceil(n / 12))
    for i, ((x, y), p) in enumerate(zip(pts, profile)):
        hi = " is-high" if p["alt"] >= 3000 else ""
        s.append(f'<g class="prof__pt{hi}"><circle cx="{x:.1f}" cy="{y:.1f}" r="5"/>'
                 f'<title>Night {p["day"]}: {escape(p["name"])}, {p["alt"]:,} m</title></g>')
        if i % step == 0 or i == n - 1:
            s.append(f'<text class="prof__day" x="{x:.1f}" y="{H - B + 20}" text-anchor="middle">D{p["day"]}</text>')
    s.append(f'<text class="prof__axis" x="{L}" y="{T - 14}" text-anchor="start">metres</text>')
    s.append("</svg>")
    return "".join(s)
