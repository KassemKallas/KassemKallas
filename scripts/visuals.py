"""Self-hosted profile graphics: badges, animated hero, research journey, collaboration map.

Everything is drawn here as plain SVG, so the profile never depends on a third-party image
service being up, and every number on the page comes from the same data.json.
"""
import datetime as dt
import html
import math
import re
import unicodedata

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
e = html.escape

THEMES = {
    "light": dict(bg="#FFFFFF", panel="#F4F6F9", ink="#0E2136", muted="#566376", line="#D6DDE6",
                  accent="#0B7A83", accent2="#7FB8BD", bar="#0E2136", award="#8A5A00", hot="#C2412D",
                  grid="#E6EBF1"),
    "dark": dict(bg="#0D1117", panel="#161B22", ink="#E6EDF3", muted="#8B98A9", line="#30363D",
                 accent="#43C3CB", accent2="#2A6F75", bar="#43C3CB", award="#F2C46B", hot="#FF7B6B",
                 grid="#1C232C"),
}


# ---------------------------------------------------------------- badges
def _text_width(s, size=11):
    """Approximate Verdana advance widths (what shields.io uses), in px at 11px."""
    w = 0.0
    for ch in s:
        if ch in "ijl.,:;|!'":
            w += 3.4
        elif ch in "frt()[] -":
            w += 4.6
        elif ch in "mwMW":
            w += 10.0
        elif ch.isdigit():
            w += 7.0
        elif ch.isupper():
            w += 7.6
        else:
            w += 6.6
    return w * size / 11


def badge(label, value, color):
    lw = round(_text_width(label) + 14)
    vw = round(_text_width(value) + 14)
    W = lw + vw
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="22" role="img" aria-label="{e(label)}: {e(value)}">'
            f'<title>{e(label)}: {e(value)}</title>'
            f'<clipPath id="r"><rect width="{W}" height="22" rx="4"/></clipPath><g clip-path="url(#r)">'
            f'<rect width="{lw}" height="22" fill="#33404F"/><rect x="{lw}" width="{vw}" height="22" fill="{color}"/></g>'
            f'<g fill="#fff" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">'
            f'<text x="{lw/2}" y="15">{e(label)}</text>'
            f'<text x="{lw+vw/2}" y="15" font-weight="bold">{e(value)}</text></g></svg>')


def badges(data):
    sm, gh = data.get("summary", {}), data.get("github", {})
    def f(n):
        return "–" if n is None else f"{n:,}"
    navy, teal = "#0E2136", "#0B7A83"
    return {
        "citations": badge("citations", f(sm.get("citations")), navy),
        "h-index": badge("h-index", f(sm.get("h")), navy),
        "i10-index": badge("i10-index", f(sm.get("i10")), navy),
        "papers": badge("papers", f(sm.get("papers")), navy),
        "stars": badge("GitHub stars", f(gh.get("stars")), teal),
        "followers": badge("followers", f(gh.get("followers")), teal),
    }


# ---------------------------------------------------------------- hero
TAGLINES = [
    "Backdoor and data-poisoning attacks on deep learning",
    "Watermarking neural networks to protect intellectual property",
    "Secure federated learning for healthcare",
]


def hero(t, sm):
    W, H = 880, 230
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Kassem Kallas, AI security scientist. A small neural network with a hidden trigger path that is detected and blocked.">']
    n = len(TAGLINES)
    cyc = 4.5 * n
    css = [f"text{{font-family:{FONT};}}",
           ".mono{font-family:" + MONO + ";}",
           f".flow{{stroke-dasharray:4 7;animation:flow 1.6s linear infinite;}}",
           "@keyframes flow{to{stroke-dashoffset:-22;}}",
           f".hot{{stroke-dasharray:160;stroke-dashoffset:160;animation:hot {cyc/2}s ease-in-out infinite;}}",
           "@keyframes hot{0%,10%{stroke-dashoffset:160;opacity:1}35%{stroke-dashoffset:0;opacity:1}55%{stroke-dashoffset:0;opacity:1}65%,100%{stroke-dashoffset:0;opacity:0}}",
           f".trig{{animation:trig {cyc/2}s ease-in-out infinite;}}",
           "@keyframes trig{0%,5%{opacity:0}12%,58%{opacity:1}68%,100%{opacity:0}}",
           f".shield{{opacity:0;animation:shield {cyc/2}s ease-in-out infinite;transform-box:fill-box;transform-origin:center;}}",
           "@keyframes shield{0%,45%{opacity:0;transform:scale(.6)}55%{opacity:1;transform:scale(1.08)}60%,85%{opacity:1;transform:scale(1)}95%,100%{opacity:0;transform:scale(1)}}",
           ".node{animation:pulse 3.2s ease-in-out infinite;}",
           "@keyframes pulse{0%,100%{opacity:.75}50%{opacity:1}}",
           "@keyframes rise{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}",
           ".in{animation:rise .9s ease-out both;}",
           ]
    for i in range(n):
        a, b = i / n * 100, (i + 1) / n * 100
        css.append(f".tl{i}{{opacity:0;animation:tl{i} {cyc}s ease-in-out infinite;}}")
        css.append(f"@keyframes tl{i}{{0%,{a:.2f}%{{opacity:0;transform:translateY(6px)}}"
                   f"{a+2.5:.2f}%,{b-2.5:.2f}%{{opacity:1;transform:none}}{b:.2f}%,100%{{opacity:0;transform:translateY(-6px)}}}}")
    css.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}.tl0{opacity:1}.shield{opacity:1}}")
    o.append("<style>" + "".join(css) + "</style>")
    o.append(f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["bg"]}" stroke="{t["line"]}"/>')
    # dot grid
    o.append(f'<defs><pattern id="g" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="{t["grid"]}"/></pattern>'
             f'<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="{t["bg"]}" stop-opacity="1"/><stop offset=".45" stop-color="{t["bg"]}" stop-opacity="0"/></linearGradient></defs>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#g)"/>')
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="url(#fade)"/>')
    # left: identity
    o.append(f'<g class="in"><text x="36" y="70" font-size="13" fill="{t["accent"]}" class="mono" letter-spacing="1.5">AI SECURITY · HEALTHCARE · DEFENSE</text>'
             f'<text x="34" y="112" font-size="38" font-weight="700" fill="{t["ink"]}">Kassem Kallas</text>'
             f'<text x="36" y="140" font-size="15" fill="{t["muted"]}">Senior Scientist &amp; Junior Professor · INSERM &amp; IMT Atlantique</text></g>')
    o.append(f'<text x="36" y="182" font-size="12" class="mono" fill="{t["muted"]}">&gt;</text>')
    for i, line in enumerate(TAGLINES):
        o.append(f'<text class="tl{i}" x="52" y="182" font-size="14" fill="{t["ink"]}">{e(line)}</text>')
    # right: network with a hidden trigger path
    layers = [[60, 95, 130, 165], [50, 85, 120, 155, 190], [72, 112, 152], [112]]
    xs = [585, 665, 745, 820]
    pts = [[(xs[i], y) for y in col] for i, col in enumerate(layers)]
    for i in range(len(pts) - 1):
        for a in pts[i]:
            for b in pts[i + 1]:
                o.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{t["line"]}" stroke-width="1"/>')
    for i in range(len(pts) - 1):
        for k, a in enumerate(pts[i]):
            b = pts[i + 1][(k * 2 + 1) % len(pts[i + 1])]
            o.append(f'<line class="flow" x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{t["accent"]}" stroke-width="1.4" opacity=".7" style="animation-delay:{-0.3*k-0.5*i:.1f}s"/>')
    path = [pts[0][3], pts[1][3], pts[2][1], pts[3][0]]
    d = "M" + " L".join(f"{x},{y}" for x, y in path)
    o.append(f'<path class="hot" d="{d}" fill="none" stroke="{t["hot"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    for col in pts:
        for (x, y) in col:
            o.append(f'<circle class="node" cx="{x}" cy="{y}" r="7" fill="{t["bg"]}" stroke="{t["accent"]}" stroke-width="2"/>')
    # trigger patch on the input
    tx, ty = 545, 156
    o.append(f'<g class="trig">')
    for j in range(3):
        for i in range(3):
            c = t["hot"] if (i + j) % 2 == 0 else t["ink"]
            o.append(f'<rect x="{tx+i*6}" y="{ty+j*6}" width="5.4" height="5.4" fill="{c}"/>')
    o.append(f'<text x="{tx+9}" y="{ty+32}" font-size="10" text-anchor="middle" class="mono" fill="{t["hot"]}">trigger</text></g>')
    # shield on the output
    sx, sy = 820, 112
    o.append(f'<g class="shield"><path d="M{sx},{sy-17} l14,5 v9 c0,9 -6,15 -14,18 c-8,-3 -14,-9 -14,-18 v-9 z" fill="{t["accent"]}"/>'
             f'<path d="M{sx-6},{sy+1} l4,4 l8,-9" fill="none" stroke="{t["bg"]}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
             f'<text x="{sx}" y="{sy+36}" font-size="10" text-anchor="middle" class="mono" fill="{t["accent"]}">blocked</text></g>')
    cites = sm.get("citations")
    stat = (f"{cites:,} citations · h-index {sm.get('h')}" if cites else "")
    o.append(f'<text x="{W-24}" y="{H-16}" font-size="10" text-anchor="end" class="mono" fill="{t["muted"]}">{e(stat)}</text>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- works helpers
def _norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def clean_name(n):
    parts = [p for p in (n or "").split() if not (len(p) == 1 and p.isupper())]
    return " ".join(parts) or n


def dedupe_works(works):
    seen, out = set(), []
    for w in sorted(works, key=lambda w: -(w.get("c") or 0)):
        k = _norm(w.get("t"))[:60]
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(w)
    return out


def paper_items(data):
    """One list of papers for every chart and list, from the same source as the headline count."""
    sc = data.get("scholar", {}).get("articles") or []
    if sc and data.get("summary", {}).get("papers_source") == "Google Scholar":
        items = [{"t": a["title"], "y": a.get("year"), "c": a.get("cites") or 0, "url": a.get("link"),
                  "v": a.get("publication", "")} for a in sc if a.get("title")]
        return items, "Google Scholar"
    items = [{"t": w["t"], "y": w.get("y"), "c": w.get("c") or 0, "url": w.get("doi") or "",
              "v": w.get("venue", "")} for w in dedupe_works(data.get("works", []))]
    return items, "OpenAlex"


def _yr(i):
    try:
        return int(i.get("y") or 0)
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------- research journey
MILESTONES = [
    (2014, "First paper · IEEE CDC"),
    (2016, "IEEE TIFS · fusion with Byzantines"),
    (2017, "Best Paper · MMEDIA"),
    (2023, "ICASSP Top 3% paper"),
    (2025, "HDR"),
    (2026, "Springer book · FLTA 2nd Best Paper"),
]


def journey(t, data):
    W, H = 880, 330
    items, src = paper_items(data)
    dated = [i for i in items if _yr(i)]
    if not dated:
        return None
    this = dt.date.today().year
    years = list(range(min(_yr(i) for i in dated), this + 1))
    counts = {y: 0 for y in years}
    for i in dated:
        if _yr(i) in counts:
            counts[_yr(i)] += 1
    top = max(counts.values()) or 1
    star = max(items, key=lambda i: i.get("c") or 0)
    undated = len(items) - len(dated)
    css = (f"text{{font-family:{FONT};}}.m{{fill:{t['muted']};}}"
           ".b{transform-box:fill-box;transform-origin:bottom;animation:grow .9s cubic-bezier(.2,.8,.2,1) both;}"
           "@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}"
           ".f{animation:fade .8s ease-out both;}@keyframes fade{from{opacity:0}to{opacity:1}}"
           ".star{animation:tw 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center;}"
           "@keyframes tw{0%,100%{transform:scale(1)}50%{transform:scale(1.25)}}"
           "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    note = f"{len(items)} papers · {src}" + (f" · {undated} without a year not shown" if undated else "")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Research journey: papers per year with milestones">',
         f"<style>{css}</style>",
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>',
         f'<text x="24" y="36" font-size="16" font-weight="700" fill="{t["ink"]}">Research journey</text>',
         f'<text x="{W-24}" y="36" font-size="11" text-anchor="end" class="m">Papers per year · {e(note)}</text>']
    cx, cw, base, span = 40, W - 80, H - 40, 120
    bw = cw / len(years)
    xpos = {y: cx + i * bw + bw / 2 for i, y in enumerate(years)}
    # milestones first so their guide lines sit behind the bars
    rows_y = [70, 92, 114]
    rows_end = [-1e9] * len(rows_y)
    for j, (y, label) in enumerate([m for m in MILESTONES if m[0] in xpos]):
        x = xpos[y]
        wlab = len(label) * 5.9 + 14
        anchor = "end" if x > W - 200 else "start"
        x0, x1 = (x - wlab, x) if anchor == "end" else (x - 4, x + wlab)
        r = next((k for k, end in enumerate(rows_end) if x0 > end + 8), len(rows_y) - 1)
        rows_end[r] = x1
        ry = rows_y[r]
        dx = -8 if anchor == "end" else 8
        o.append(f'<g class="f" style="animation-delay:{.6+j*.15:.2f}s"><line x1="{x:.1f}" y1="{ry+4}" x2="{x:.1f}" y2="{base-2}" stroke="{t["award"]}" stroke-width="1" stroke-dasharray="2 3" opacity=".6"/>'
                 f'<circle cx="{x:.1f}" cy="{ry}" r="4" fill="{t["award"]}"/>'
                 f'<text x="{x+dx:.1f}" y="{ry+4}" font-size="11" text-anchor="{anchor}" fill="{t["ink"]}">{e(label)}</text></g>')
    o.append(f'<line x1="{cx}" y1="{base+.5}" x2="{cx+cw}" y2="{base+.5}" stroke="{t["line"]}"/>')
    for i, y in enumerate(years):
        w = bw * .56
        x = xpos[y] - w / 2
        n = counts[y]
        if n:
            h = span * n / top
            fill = t["accent2"] if y == this else t["accent"]
            o.append(f'<rect class="b" style="animation-delay:{i*0.06:.2f}s" x="{x:.1f}" y="{base-h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" fill="{fill}"/>')
            o.append(f'<text class="f" x="{xpos[y]:.1f}" y="{base-h-6:.1f}" font-size="11" font-weight="700" text-anchor="middle" fill="{t["ink"]}">{n}</text>')
        o.append(f'<text x="{xpos[y]:.1f}" y="{base+15}" font-size="10" text-anchor="middle" class="m">{y}</text>')
    if counts.get(this):
        o.append(f'<rect x="{W-150}" y="50" width="10" height="10" rx="2" fill="{t["accent2"]}"/>'
                 f'<text x="{W-135}" y="59" font-size="10.5" class="m">{this} so far</text>')
    if _yr(star) in xpos:
        x = xpos[_yr(star)]
        title = star["t"] if len(star["t"]) <= 52 else star["t"][:51] + "…"
        sy = base - span * counts[_yr(star)] / top - 30
        anchor, dx = ("end", -12) if x > W / 2 else ("start", 12)
        o.append(f'<g class="f" style="animation-delay:1.4s"><path class="star" d="M{x:.1f},{sy-7} l3,6 6.5,.9 -4.7,4.6 1.1,6.5 -5.9,-3.1 -5.9,3.1 1.1,-6.5 -4.7,-4.6 6.5,-.9z" fill="{t["hot"]}"/>'
                 f'<text x="{x+dx:.1f}" y="{sy+5}" font-size="10.5" text-anchor="{anchor}" fill="{t["hot"]}">Most cited: {e(title)} · {star.get("c",0):,}</text></g>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- collaboration map
SHORT = {"national institute of standards and technology": "NIST",
         "centre national de la recherche scientifique": "CNRS",
         "institut national de la sante et de la recherche medicale": "INSERM", "inserm": "INSERM",
         "thales france": "Thales", "imt atlantique": "IMT Atlantique", "university of siena": "University of Siena",
         "institut national de recherche en informatique et en automatique": "Inria",
         "politecnico di torino": "Politecnico di Torino"}


def short_inst(name):
    n = _norm(name)
    for k, v in SHORT.items():
        if n.startswith(k):
            return v
    return name or "Other"


def network(t, works, me_id):
    W, H = 880, 500
    works = dedupe_works(works)
    people = {}
    for wi, w in enumerate(works):
        for aid, name, inst in w.get("a", []):
            key = _norm(clean_name(name)).split()
            key = (key[-1] + " " + key[0][0]) if key else aid
            if aid == me_id or key == "kallas k":
                continue
            p = people.setdefault(key, {"name": clean_name(name), "works": set(), "inst": {}})
            p["works"].add(wi)
            si = short_inst(inst)
            p["inst"][si] = p["inst"].get(si, 0) + 1
    if not people:
        return None
    for p in people.values():
        p["n"] = len(p["works"])
        p["group"] = max(p["inst"].items(), key=lambda kv: kv[1])[0]
    groups = {}
    for k, p in people.items():
        groups.setdefault(p["group"], []).append(k)
    def weight(g):
        return len(set().union(*(people[k]["works"] for k in groups[g])))
    order = sorted(groups, key=lambda g: (-weight(g), g))
    if len(order) > 8:
        rest = [k for g in order[7:] for k in groups.pop(g)]
        groups["Other"] = groups.get("Other", []) + rest
        order = [g for g in order[:7] if g != "Other"] + ["Other"]
    CX, CY, RX, RY = W / 2, 262, 290, 145
    mx = max(p["n"] for p in people.values())
    gw = {g: weight(g) for g in order}
    gmx = max(gw.values())
    css = (f"text{{font-family:{FONT};}}.m{{fill:{t['muted']};}}"
           ".e{stroke-dasharray:5 7;animation:flow 1.8s linear infinite;}@keyframes flow{to{stroke-dashoffset:-24;}}"
           ".n{animation:pop .7s cubic-bezier(.2,.8,.2,1.3) both;transform-box:fill-box;transform-origin:center;}"
           "@keyframes pop{from{transform:scale(0)}to{transform:scale(1)}}"
           ".me{animation:halo 3s ease-in-out infinite;transform-box:fill-box;transform-origin:center;}"
           "@keyframes halo{0%,100%{transform:scale(1);opacity:.4}50%{transform:scale(1.4);opacity:0}}"
           "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Collaboration map: {len(people)} co-authors grouped by institution">',
         f"<style>{css}</style>",
         f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>',
         f'<text x="24" y="36" font-size="16" font-weight="700" fill="{t["ink"]}">Collaboration map</text>',
         f'<text x="{W-24}" y="36" font-size="11" text-anchor="end" class="m">{len(people)} co-authors · {len(order)} institution groups · OpenAlex</text>']
    spokes, clusters, labels = [], [], []
    for gi, g in enumerate(order):
        ang = -math.pi / 2 + (gi + .5) * 2 * math.pi / len(order)
        hx, hy = CX + RX * math.cos(ang), CY + RY * math.sin(ang)
        members = sorted(groups[g], key=lambda k: (-people[k]["n"], k))
        R = 16 + 7.5 * math.sqrt(len(members))
        spokes.append(f'<line class="e" style="animation-delay:{-gi*.25:.2f}s" x1="{CX}" y1="{CY}" x2="{hx:.1f}" y2="{hy:.1f}" '
                      f'stroke="{t["accent"]}" stroke-width="{1+3.5*gw[g]/gmx:.2f}" opacity="{.35+.5*gw[g]/gmx:.2f}" stroke-linecap="round"/>')
        clusters.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="{R:.1f}" fill="{t["panel"]}" stroke="{t["line"]}"/>')
        for mi, k in enumerate(members):
            if len(members) == 1:
                px, py = hx, hy
            else:
                rr = (R - 9) * math.sqrt((mi + .5) / len(members))
                aa = mi * 2.39996
                px, py = hx + rr * math.cos(aa), hy + rr * math.sin(aa)
            r = 3.2 + 5.5 * math.sqrt(people[k]["n"] / mx)
            clusters.append(f'<circle class="n" style="animation-delay:{.3+gi*.12+mi*.03:.2f}s" cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" '
                            f'fill="{t["accent"]}" fill-opacity="{.35+.65*people[k]["n"]/mx:.2f}"><title>{e(people[k]["name"])} · {people[k]["n"]} papers</title></circle>')
        def surname(n):
            parts = [x for x in n.split() if not x.endswith(".")]
            return " ".join(parts[1:]) if len(parts) > 1 else n
        names = [surname(people[k]["name"]) for k in members[:3]]
        more = len(members) - len(names)
        lines = [(g, f"{gw[g]} paper{'s' if gw[g] != 1 else ''}"), (", ".join(names) + (f" +{more}" if more > 0 else ""), None)]
        lx = min(max(hx, 110), W - 110)
        down = math.sin(ang) > -.2
        ly = hy + R + 16 if down else hy - R - 22
        labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" font-size="12" font-weight="700" text-anchor="middle" fill="{t["ink"]}">{e(lines[0][0])}'
                      f'<tspan font-weight="400" class="m"> · {e(lines[0][1])}</tspan></text>'
                      f'<text x="{lx:.1f}" y="{ly+14:.1f}" font-size="10.5" text-anchor="middle" class="m">{e(lines[1][0])}</text>')
    o += spokes + clusters + labels
    o.append(f'<circle class="me" cx="{CX}" cy="{CY}" r="30" fill="{t["accent"]}"/>'
             f'<circle cx="{CX}" cy="{CY}" r="28" fill="{t["ink"]}"/>'
             f'<text x="{CX}" y="{CY+5}" font-size="15" font-weight="700" text-anchor="middle" fill="{t["bg"]}">KK</text>')
    o.append(f'<text x="24" y="{H-16}" font-size="10" class="m">Dot size = papers together · spoke width = papers with that group · '
             f'group = co-author’s most frequent affiliation on those papers</text>')
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- README lists
def _md(s):
    return re.sub(r"([\[\]|*_`])", r"\\\1", (s or "").strip())


def pub_lists(data):
    """Markdown for the auto-updated 'Latest' and 'Most cited' lists."""
    items, src = paper_items(data)
    latest = sorted(items, key=lambda i: (_yr(i), i["c"]), reverse=True)[:6]
    cited = sorted(items, key=lambda i: i["c"], reverse=True)[:3]
    def line(i, cites=False):
        v = re.sub(r"^\d{4}\s+", "", (i["v"] or "").strip())
        v = re.split(r",|\s\d", v)[0].strip()[:70]
        title = f'[{_md(i["t"])}]({i["url"]})' if i.get("url") else _md(i["t"])
        tail = f" · **{i['c']:,} citations**" if cites else ""
        return f"- `{_yr(i) or '—'}` {title}" + (f" · *{_md(v)}*" if v else "") + tail
    out = ["**Latest**", ""] + [line(i) for i in latest] + ["", "**Most cited**", ""] + [line(i, True) for i in cited]
    out += ["", f"<sub>Updated automatically from {src} on {data.get('updated', '')}.</sub>"]
    return "\n".join(out)
