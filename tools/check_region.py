"""Validate one hive's content against content/SCHEMA.md.

Usage: python tools/check_region.py <region-slug> [--wiki]
--wiki also confirms every `wiki` title exists on English Wikipedia.
"""
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "content"
THEMES = set("road-trips treks-and-walks monasteries pilgrimages wildlife-and-birds snow-and-winter honeymoons "
             "family-holidays homestays-and-villages food-and-tea festivals photography adventure-sports "
             "wellness-and-yoga".split())
KINDS = set("culture spiritual nature wildlife food adventure trek craft village wellness".split())
TIERS = {"saver", "comfort", "signature"}
STAY_TIERS = {"budget", "mid", "luxury"}
BANNED = ["nestled", "breathtaking", "hidden gem", "paradise", "tapestry", "embark", "delve", "unleash",
          "vibrant", "bustling", "mesmeriz", "stunning", "magical", "heaven on earth", "feast for the eyes",
          "something for everyone", "whether you're", "look no further", "ultimate guide", "in this blog",
          "in conclusion", "unforgettable", "world-class", "seamless", "elevate", "immerse", "timeless",
          "boasts", "abode of", "!"]
errors, warns = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def load(p):
    try:
        return json.loads(Path(p).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(str(p), f"invalid JSON ({e})")
        return None


def months(where, v):
    if not (isinstance(v, list) and len(v) == 12 and all(x in (0, 1, 2) for x in v)):
        err(where, "best_months must be 12 ints of 0/1/2")


def faqs(where, v, n):
    if not isinstance(v, list) or len(v) != n:
        err(where, f"needs exactly {n} faqs (has {len(v) if isinstance(v, list) else 0})")
        return
    for f in v:
        if not f.get("q") or not f.get("a"):
            err(where, "faq missing q/a")


def heading(where, t):
    if t and t.rstrip().endswith("."):
        err(where, f"heading ends with full stop: {t!r}")


def scan_banned(where, obj):
    text = json.dumps(obj, ensure_ascii=False).lower()
    for b in BANNED:
        if b in text:
            warns.append(f"{where}: banned word/phrase '{b}'")
    for b in ("offbeat", "curated", "iconic"):
        if text.count(b) > 1:
            warns.append(f"{where}: '{b}' used {text.count(b)} times (max once)")


def main():
    r = sys.argv[1]
    base = ROOT / r
    wiki_titles = []
    reg = load(base / "region.json")
    places, stays, fests = {}, {}, {}
    for p in sorted((base / "places").glob("*.json")):
        d = load(p)
        if d:
            places[d["slug"]] = d
    for s in load(base / "stays.json") or []:
        stays[s["slug"]] = s
    for f in load(base / "festivals.json") or []:
        fests[f["slug"]] = f

    if reg:
        months("region", reg.get("best_months"))
        faqs("region", reg.get("faqs"), 9)
        if len(reg.get("highlights", [])) != 6:
            err("region", "needs 6 highlights")
        if len(reg.get("months", [])) != 12:
            err("region", "needs 12 months")
        if len((reg.get("story") or {}).get("chapters", [])) != 4:
            err("region", "story needs 4 chapters")
        if len(reg.get("glossary", [])) != 8:
            err("region", "needs 8 glossary words")
        if len(reg.get("money_savers", [])) != 6:
            err("region", "needs 6 money_savers")
        if {b.get("tier") for b in reg.get("budget", [])} != TIERS:
            err("region", "budget needs saver, comfort, signature rows")
        for m in reg.get("months", []):
            if m.get("price_level") not in ("low", "shoulder", "peak"):
                err(f"region month {m.get('month')}", "price_level must be low|shoulder|peak")
            if m.get("crowd") not in ("low", "medium", "high"):
                err(f"region month {m.get('month')}", "crowd must be low|medium|high")
            for g in m.get("go", []):
                if g not in places:
                    err(f"region month {m.get('month')}", f"unknown place '{g}'")
            for e in m.get("events", []):
                if e not in fests:
                    err(f"region month {m.get('month')}", f"unknown festival '{e}'")
        wiki_titles.append(reg.get("wiki"))
        scan_banned("region", reg)

    exp_slugs = set()
    for slug, d in places.items():
        w = f"place {slug}"
        months(w, d.get("best_months"))
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("tagline"))
        if not isinstance(d.get("altitude_m"), (int, float)):
            err(w, "altitude_m must be a number")
        fn = d.get("field_notes", [])
        if not 2 <= len(fn) <= 3 or not all(f.get("fact") and f.get("source") for f in fn):
            err(w, "needs 2–3 field_notes with fact and source")
        if not (d.get("local_word") or {}).get("word"):
            err(w, "needs local_word")
        if not 4 <= len(d.get("costs", [])) <= 7:
            err(w, "needs 5–6 costs rows")
        for t in d.get("themes", []):
            if t not in THEMES:
                err(w, f"unknown theme '{t}'")
        for n in d.get("nearby", []):
            if n not in places:
                err(w, f"unknown nearby '{n}'")
        for s in d.get("stays", []):
            if s not in stays:
                err(w, f"unknown stay '{s}'")
        ex = d.get("experiences", [])
        if len(ex) != 3:
            err(w, f"needs 3 experiences (has {len(ex)})")
        for e in ex:
            heading(f"{w} exp", e.get("title"))
            faqs(f"{w} exp {e.get('slug')}", e.get("faqs"), 3)
            if e.get("kind") not in KINDS:
                err(f"{w} exp {e.get('slug')}", f"unknown kind '{e.get('kind')}'")
            if e["slug"] in exp_slugs:
                err(w, f"duplicate experience slug {e['slug']}")
            exp_slugs.add(e["slug"])
            if e.get("wiki"):
                wiki_titles.append(e["wiki"])
        wiki_titles.append(d.get("wiki"))
        scan_banned(w, d)

    tiers = {"saver": 0, "comfort": 0, "signature": 0}
    for p in sorted((base / "journeys").glob("*.json")):
        d = load(p)
        if not d:
            continue
        w = f"journey {d.get('slug')}"
        if d.get("tier") not in TIERS:
            err(w, "tier must be saver|comfort|signature")
        else:
            tiers[d["tier"]] += 1
        if not isinstance(d.get("price_from_inr"), int):
            err(w, "price_from_inr must be an integer")
        months(w, d.get("best_months"))
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("title"))
        total = sum(s.get("nights", 0) for s in d.get("stops", []))
        if total != d.get("nights"):
            err(w, f"stop nights {total} != nights {d.get('nights')}")
        if len(d.get("days", [])) != d.get("nights", 0) + 1:
            err(w, "days must equal nights + 1")
        for day in d.get("days", []):
            if day.get("place") and day["place"] not in places:
                err(w, f"day {day.get('day')}: unknown place '{day['place']}'")
        for s in d.get("stops", []):
            if s["place"] not in places:
                err(w, f"unknown stop '{s['place']}'")
        for s in d.get("stays", []):
            if s not in stays:
                err(w, f"unknown stay '{s}'")
        for t in d.get("themes", []):
            if t not in THEMES:
                err(w, f"unknown theme '{t}'")
        scan_banned(w, d)

    for slug, s in stays.items():
        w = f"stay {slug}"
        faqs(w, s.get("faqs"), 3)
        if s.get("tier") not in STAY_TIERS:
            err(w, "tier must be budget|mid|luxury")
        if s.get("place") not in places:
            err(w, f"unknown place '{s.get('place')}'")
        if s.get("wiki"):
            wiki_titles.append(s["wiki"])
        scan_banned(w, s)

    for p in sorted((base / "guides").glob("*.json")):
        d = load(p)
        if not d:
            continue
        w = f"guide {d.get('slug')}"
        faqs(w, d.get("faqs"), 9)
        heading(w, d.get("title"))
        words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in d.get("sections", []))
        if words < 1000:
            warns.append(f"{w}: only {words} words")
        for s in d.get("sections", []):
            heading(w, s.get("heading"))
        for rp in d.get("related_places", []):
            if rp not in places:
                err(w, f"unknown related place '{rp}'")
        scan_banned(w, d)

    for slug, f in fests.items():
        w = f"festival {slug}"
        faqs(w, f.get("faqs"), 4)
        if f.get("place") not in places:
            err(w, f"unknown place '{f.get('place')}'")
        if f.get("wiki"):
            wiki_titles.append(f["wiki"])
        scan_banned(w, f)

    routes = load(base / "routes.json") or []
    for rt in routes:
        w = f"route {rt.get('slug')}"
        faqs(w, rt.get("faqs"), 4)
        for k in ("from", "to"):
            if rt.get(k) not in places:
                err(w, f"unknown {k} '{rt.get(k)}'")
        scan_banned(w, rt)

    if "--wiki" in sys.argv:
        titles = sorted({t for t in wiki_titles if t})
        for i in range(0, len(titles), 40):
            q = urllib.parse.urlencode({"action": "query", "titles": "|".join(titles[i:i + 40]),
                                        "redirects": 1, "format": "json", "formatversion": 2})
            req = urllib.request.Request("https://en.wikipedia.org/w/api.php?" + q,
                                         headers={"User-Agent": "HimalayaHivesBuild/1.0 (content check)"})
            data = json.load(urllib.request.urlopen(req, timeout=30))
            for pg in data["query"]["pages"]:
                if pg.get("missing") or pg.get("invalid"):
                    err("wiki", f"no Wikipedia article titled {pg.get('title')!r} (use '' or fix)")

    n_j = len(list((base / "journeys").glob("*.json")))
    print(f"places={len(places)} experiences={len(exp_slugs)} stays={len(stays)} festivals={len(fests)} "
          f"routes={len(routes)} journeys={n_j} {tiers} guides={len(list((base / 'guides').glob('*.json')))}")
    for w in warns:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print("OK" if not errors else f"{len(errors)} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
