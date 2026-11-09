"""Build the research and code dashboard shown on the GitHub profile.

Runs daily in GitHub Actions. Pulls live numbers from:
  - GitHub REST API: public repositories, stars, forks, followers
  - Semantic Scholar Graph API: citations, h-index, paper count
  - OpenAlex API: citations per year, works count, h-index
Writes assets/dashboard-light.svg, assets/dashboard-dark.svg and assets/data.json.
If a source is unreachable, the last saved values are reused so the card never breaks.
Standard library only.
"""
import datetime as dt
import html
import json
import os
import time
import urllib.request

USER = "KassemKallas"
S2_AUTHOR = "3192444"            # Semantic Scholar author id
OPENALEX_AUTHOR = "A5046279472"  # OpenAlex author id (ORCID 0000-0001-7689-4125)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
DATA = os.path.join(ASSETS, "data.json")


def get(url, token=None, tries=4):
    headers = {"User-Agent": f"{USER}-profile-dashboard", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
                return json.load(r)
        except Exception as e:  # rate limits and transient errors
            print(f"warn: {url} -> {e}")
            time.sleep(5 * (i + 1))
    return None


def load_previous():
    try:
        with open(DATA) as f:
            return json.load(f)
    except Exception:
        return {}


def github_stats(prev):
    token = os.environ.get("GITHUB_TOKEN")
    user = get(f"https://api.github.com/users/{USER}", token)
    repos = get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner", token)
    if not user or repos is None:
        return prev.get("github", {})
    own = [r for r in repos if not r.get("fork")]
    top = sorted(own, key=lambda r: (r["stargazers_count"], r["forks_count"]), reverse=True)[:5]
    return {
        "repos": len(own),
        "stars": sum(r["stargazers_count"] for r in own),
        "forks": sum(r["forks_count"] for r in own),
        "followers": user.get("followers", 0),
        "top": [{"name": r["name"], "stars": r["stargazers_count"], "forks": r["forks_count"]} for r in top],
    }


def s2_stats(prev):
    a = get(f"https://api.semanticscholar.org/graph/v1/author/{S2_AUTHOR}?fields=citationCount,hIndex,paperCount")
    if not a or "citationCount" not in a:
        return prev.get("s2", {})
    return {"citations": a["citationCount"], "h": a["hIndex"], "papers": a["paperCount"]}


def openalex_stats(prev):
    a = get(f"https://api.openalex.org/authors/{OPENALEX_AUTHOR}?mailto=noreply@github.com")
    if not a or "counts_by_year" not in a:
        return prev.get("openalex", {})
    years = sorted(a["counts_by_year"], key=lambda y: y["year"])
    return {
        "citations": a["cited_by_count"],
        "works": a["works_count"],
        "h": a.get("summary_stats", {}).get("h_index"),
        "by_year": [{"year": y["year"], "cites": y["cited_by_count"]} for y in years],
    }


THEMES = {
    "light": dict(bg="#FFFFFF", panel="#F4F6F9", ink="#0E2136", muted="#566376", line="#D6DDE6",
                  accent="#0B7A83", accent2="#7FB8BD", bar="#0E2136", award="#8A5A00"),
    "dark": dict(bg="#0D1117", panel="#161B22", ink="#E6EDF3", muted="#8B98A9", line="#30363D",
                 accent="#43C3CB", accent2="#2A6F75", bar="#43C3CB", award="#F2C46B"),
}
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"


def fmt(n):
    if n is None:
        return "–"
    return f"{n:,}"


def svg(data, t):
    W, H = 880, 380
    e = html.escape
    gh, s2, oa = data.get("github", {}), data.get("s2", {}), data.get("openalex", {})
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
           f'aria-label="Research and code dashboard for Kassem Kallas">',
           f'<style>text{{font-family:{FONT};}} .n{{font-weight:700;}} .m{{fill:{t["muted"]};}}</style>',
           f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>']
    # header
    out.append(f'<text x="24" y="36" font-size="16" class="n" fill="{t["ink"]}">Research &amp; code dashboard</text>')
    out.append(f'<text x="{W-24}" y="36" font-size="12" text-anchor="end" class="m">Updated {e(data.get("updated",""))} · refreshes daily</text>')
    # pixel trigger motif
    for j in range(2):
        for i in range(2):
            c = t["accent"] if (i + j) % 2 else t["ink"]
            out.append(f'<rect x="{262+i*6}" y="{25+j*6}" width="5" height="5" fill="{c}"/>')
    # stat tiles
    tiles = [
        (fmt(s2.get("citations")), "Citations", "Semantic Scholar"),
        (fmt(s2.get("h") or oa.get("h")), "h-index", "Semantic Scholar"),
        (fmt(oa.get("works") or s2.get("papers")), "Indexed works", "OpenAlex"),
        (fmt(gh.get("stars")), "GitHub stars", "own repositories"),
        (fmt(gh.get("repos")), "Public repos", "GitHub"),
        (fmt(gh.get("followers")), "Followers", "GitHub"),
    ]
    gap, x0, y0 = 10, 24, 56
    tw = (W - 2 * x0 - 5 * gap) / 6
    for k, (num, label, src) in enumerate(tiles):
        x = x0 + k * (tw + gap)
        out.append(f'<rect x="{x:.1f}" y="{y0}" width="{tw:.1f}" height="78" rx="8" fill="{t["panel"]}"/>')
        out.append(f'<rect x="{x}" y="{y0}" width="4" height="78" rx="2" fill="{t["accent"]}"/>')
        out.append(f'<text x="{x+16}" y="{y0+34}" font-size="26" class="n" fill="{t["ink"]}">{e(num)}</text>')
        out.append(f'<text x="{x+16}" y="{y0+54}" font-size="12" fill="{t["ink"]}">{e(label)}</text>')
        out.append(f'<text x="{x+16}" y="{y0+69}" font-size="10" class="m">{e(src)}</text>')
    # citations per year chart (left)
    by = [y for y in oa.get("by_year", []) if y["year"] >= dt.date.today().year - 9]
    cx, cy, cw, ch = 24, 160, 470, 196
    out.append(f'<text x="{cx}" y="{cy+8}" font-size="13" class="n" fill="{t["ink"]}">Citations per year</text>')
    out.append(f'<text x="{cx+cw}" y="{cy+8}" font-size="10" text-anchor="end" class="m">OpenAlex · {fmt(oa.get("citations"))} total</text>')
    if by:
        top = max(y["cites"] for y in by) or 1
        base = cy + ch - 18
        span = ch - 54
        bw = cw / len(by)
        out.append(f'<line x1="{cx}" y1="{base+0.5}" x2="{cx+cw}" y2="{base+0.5}" stroke="{t["line"]}"/>')
        this_year = dt.date.today().year
        for i, y in enumerate(by):
            h = max(2, span * y["cites"] / top)
            x = cx + i * bw + bw * 0.18
            w = bw * 0.64
            fill = t["accent2"] if y["year"] == this_year else t["bar"]
            out.append(f'<rect x="{x:.1f}" y="{base-h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="2" fill="{fill}"/>')
            out.append(f'<text x="{x+w/2:.1f}" y="{base-h-5:.1f}" font-size="10" text-anchor="middle" fill="{t["ink"]}">{y["cites"]}</text>')
            out.append(f'<text x="{x+w/2:.1f}" y="{base+14:.1f}" font-size="10" text-anchor="middle" class="m">{y["year"]}</text>')
        out.append(f'<rect x="{cx+150}" y="{cy}" width="9" height="9" rx="2" fill="{t["accent2"]}"/>')
        out.append(f'<text x="{cx+164}" y="{cy+8}" font-size="10" class="m">{this_year} so far</text>')
    # top repositories (right)
    rx, ry, rw = 530, 160, 326
    out.append(f'<text x="{rx}" y="{ry+8}" font-size="13" class="n" fill="{t["ink"]}">Most starred repositories</text>')
    reps = gh.get("top", [])
    m = max([r["stars"] for r in reps] + [1])
    for i, r in enumerate(reps):
        y = ry + 30 + i * 34
        name = r["name"] if len(r["name"]) <= 34 else r["name"][:33] + "…"
        out.append(f'<text x="{rx}" y="{y}" font-size="11" fill="{t["ink"]}">{e(name)}</text>')
        out.append(f'<rect x="{rx}" y="{y+6}" width="{rw-60}" height="7" rx="3.5" fill="{t["panel"]}"/>')
        out.append(f'<rect x="{rx}" y="{y+6}" width="{max(4,(rw-60)*r["stars"]/m):.1f}" height="7" rx="3.5" fill="{t["accent"]}"/>')
        out.append(f'<text x="{rx+rw}" y="{y+13}" font-size="11" text-anchor="end" fill="{t["ink"]}">★ {r["stars"]} · ⑂ {r["forks"]}</text>')
    out.append("</svg>")
    return "\n".join(out)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    prev = load_previous()
    data = {
        "updated": dt.datetime.utcnow().strftime("%Y-%m-%d"),
        "github": github_stats(prev),
        "s2": s2_stats(prev),
        "openalex": openalex_stats(prev),
    }
    with open(DATA, "w") as f:
        json.dump(data, f, indent=2)
    for name, theme in THEMES.items():
        with open(os.path.join(ASSETS, f"dashboard-{name}.svg"), "w") as f:
            f.write(svg(data, theme))
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()
