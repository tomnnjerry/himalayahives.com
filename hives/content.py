"""In-memory catalogue built from content/*.json.

Every page on the site is rendered from this catalogue. In DEBUG the catalogue
reloads when any content file changes, so writers see edits on refresh.
"""
import json
import re
from collections import OrderedDict
from pathlib import Path

from django.conf import settings
from django.urls import reverse

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MONTH_SHORT = [m[:3] for m in MONTHS]
REGION_ORDER = ["kashmir", "ladakh", "himachal", "spiti", "garhwal", "kumaon", "nepal", "darjeeling", "sikkim",
                "bhutan", "arunachal"]
# Each hive wears the colours it is known for.
# grad = dark ground (3 stops), foil = metallic accent (light, mid, deep), ink = accent text on light, tint = light wash
LANDS = {
    "kashmir": {"palette": "Dal Lake blue and chinar copper", "icon_note": "shikara and chinar leaf",
                "grad": ("#071A36", "#0E2F5E", "#1B4C86"), "foil": ("#FFD9BE", "#EE8447", "#B9481B"),
                "ink": "#A2420F", "tint": "#E6EDF7"},
    "ladakh": {"palette": "Pangong teal and Raktsey apricot", "icon_note": "gompa on a ridge",
               "grad": ("#03262B", "#08484F", "#0F6F77"), "foil": ("#FFEBC4", "#F5B866", "#C77E23"),
               "ink": "#8A5A12", "tint": "#E0F0F0"},
    "himachal": {"palette": "Deodar green and Kinnaur apple red", "icon_note": "kath-kuni tower temple",
                 "grad": ("#0A231A", "#12402D", "#1C5E40"), "foil": ("#FFD3CC", "#E8545A", "#A92330"),
                 "ink": "#A3242F", "tint": "#E3EFE7"},
    "spiti": {"palette": "Umber scree and Chandratal turquoise", "icon_note": "cliff-top gompa",
              "grad": ("#21160C", "#3D2A18", "#5C4026"), "foil": ("#D2FFF6", "#45D3C1", "#129080"),
              "ink": "#0E6E62", "tint": "#F2EBE1"},
    "garhwal": {"palette": "Kedar granite and marigold", "icon_note": "temple spire under a peak",
                "grad": ("#121C24", "#1F3340", "#2F4B5C"), "foil": ("#FFEBB0", "#F7AE2A", "#C5730A"),
                "ink": "#975400", "tint": "#E7EDF0"},
    "kumaon": {"palette": "Oak moss and Aipan rice-white", "icon_note": "Aipan lotus",
               "grad": ("#141F0B", "#2A3A16", "#435923"), "foil": ("#FFFFFF", "#F1E7D2", "#C7B184"),
               "ink": "#5E6B1E", "tint": "#EEF0E2"},
    "nepal": {"palette": "Rhododendron wine and gilt bronze", "icon_note": "Boudhanath stupa",
              "grad": ("#2A0618", "#4C0E2E", "#721A45"), "foil": ("#FFF0BC", "#E6B74E", "#A87516"),
              "ink": "#8C5A0C", "tint": "#F5E6EC"},
    "darjeeling": {"palette": "First-flush olive and toy-train blue", "icon_note": "toy train and tea leaf",
                   "grad": ("#191F06", "#2F3A0E", "#4A5A19"), "foil": ("#D7EEFF", "#5EACEA", "#2569A8"),
                   "ink": "#22609C", "tint": "#EFF1DE"},
    "sikkim": {"palette": "Khangchendzonga violet and orchid", "icon_note": "orchid",
               "grad": ("#150C2C", "#2A1A4E", "#432A73"), "foil": ("#FFDBF3", "#E77CCA", "#AF3B8E"),
               "ink": "#9C2E7D", "tint": "#EEE9F6"},
    "bhutan": {"palette": "Monk-robe maroon and Druk saffron", "icon_note": "dzong",
               "grad": ("#240607", "#3E0E11", "#5E181B"), "foil": ("#FFF4A8", "#F2C51E", "#B88A06"),
               "ink": "#8A6400", "tint": "#F6E9E7"},
    "arunachal": {"palette": "Dawn plum and Siang coral", "icon_note": "rising sun over ridges",
                  "grad": ("#230A24", "#3E1240", "#5E1E5C"), "foil": ("#FFDCC8", "#FF8C5E", "#C6512A"),
                  "ink": "#B0431D", "tint": "#F4E8F1"},
}
for _slug, _p in LANDS.items():
    _p["accent"] = _p["foil"][1]
    _p["ground"] = _p["grad"][1]

TIERS = OrderedDict([
    ("saver", {"name": "Saver", "line": "Shared jeeps, state buses, homestays and honest numbers",
               "long": "The affordable Himalaya. Shared jeeps and state buses, homestays and government tourist "
                       "bungalows, local food. Simple, safe, and planned so the money goes to the valley."}),
    ("comfort", {"name": "Comfort", "line": "Private car with driver, good hotels, the best homestays",
                 "long": "A private car and a driver who knows the road, good three and four star hotels and the "
                         "best homestays, with time built in for altitude and weather."}),
    ("signature", {"name": "Signature", "line": "The best lodges in the range and a private guide",
                   "long": "The best hotels and lodges each valley has, a private guide, and slow days. The "
                           "Himalaya at its most comfortable."}),
])
BUDGET_BANDS = [(15000, "Under ₹15,000"), (25000, "Under ₹25,000"), (40000, "Under ₹40,000")]

KINDS = OrderedDict([
    ("culture", ("Culture", "Gompas, dzongs, old bazaars and the people who keep them", "Guided walks, festival days and evenings with music: the history of each valley told on site.")),
    ("spiritual", ("Spiritual", "Monasteries, dhams, stupas and shrines", "Rituals at their own hours, with guides who explain what you see and keep the visit respectful.")),
    ("nature", ("Nature", "Lakes, meadows, glaciers and passes", "Viewpoints at the right hour, flower meadows in season and quiet days outdoors.")),
    ("trek", ("Treks", "Day hikes to two-week trails", "Walks graded honestly by hours, height gain and terrain, with local guides and porters where they help.")),
    ("wildlife", ("Wildlife", "Snow leopard, red panda, cranes, birds", "Wildlife trips timed to the season, with trackers who live in the valley.")),
    ("village", ("Village life", "Homestays, farms and harvests", "Nights in family homes, a hand in the fields and the kitchen, and money that stays in the village.")),
    ("food", ("Food", "Momos, wazwan, thukpa and tea", "Kitchens, markets and tea gardens: the cheapest and best way to understand a valley.")),
    ("adventure", ("Adventure", "Rafting, paragliding, skiing and high roads", "Active days with certified operators, honest about risk, weather and season.")),
    ("craft", ("Craft", "Weavers, carvers, thangka painters", "Workshop visits with the makers of pashmina, Kullu shawls, thangkas and yathra. No commission on what you buy.")),
    ("wellness", ("Wellness", "Yoga, hot springs and rest", "Yoga in Rishikesh, hot springs in the hills and slow days built into the route.")),
])

_cache = {"stamp": None, "cat": None}


def _read(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def _stamp(root):
    return max((p.stat().st_mtime for p in root.rglob("*.json")), default=0)


def catalogue():
    root = Path(settings.CONTENT_DIR)
    if _cache["cat"] is None or settings.DEBUG:
        stamp = _stamp(root)
        if stamp != _cache["stamp"]:
            _cache["cat"] = Catalogue(root)
            _cache["stamp"] = stamp
    return _cache["cat"]


def month_bar(best):
    """[{'m': 'Jan', 'v': 2}, ...] for the 12-month strip."""
    best = best or [0] * 12
    return [{"m": MONTH_SHORT[i], "full": MONTHS[i], "v": best[i] if i < len(best) else 0} for i in range(12)]


def best_range(best):
    """'Oct – Mar' style label from a 12-int array (rating 2 = best)."""
    if not best:
        return ""
    good = {i for i, v in enumerate(best) if v == 2} or {i for i, v in enumerate(best) if v >= 1}
    if not good:
        return ""
    if len(good) == 12:
        return "All year"
    runs = []  # runs on a circular calendar, e.g. Oct..Mar
    for i in range(12):
        if i in good and (i - 1) % 12 not in good:
            run, j = [i], (i + 1) % 12
            while j in good:
                run.append(j)
                j = (j + 1) % 12
            runs.append(run)
    labels = []
    for run in runs:
        labels.append(MONTH_SHORT[run[0]] if len(run) == 1 else f"{MONTH_SHORT[run[0]]} – {MONTH_SHORT[run[-1]]}")
    return " · ".join(labels)


class Catalogue:
    def __init__(self, root):
        self.root = root
        self.themes = OrderedDict((t["slug"], t) for t in _read(root / "themes.json"))
        img_file = root / "images.json"
        self.images = _read(img_file) if img_file.exists() else {}
        self.regions = OrderedDict()
        self.places = OrderedDict()
        self.experiences = OrderedDict()
        self.journeys = OrderedDict()
        self.stays = OrderedDict()
        self.guides = OrderedDict()
        self.festivals = OrderedDict()
        self.routes = OrderedDict()
        for slug in REGION_ORDER:
            base = root / slug
            if (base / "region.json").exists():
                self._load_region(slug, base)
        self.posts = OrderedDict()
        for p in (root / "journal").glob("*.json") if (root / "journal").exists() else []:
            d = _read(p)
            d["url"] = reverse("post", args=[d["slug"]])
            self.posts[d["slug"]] = d
        self.posts = OrderedDict(sorted(self.posts.items(), key=lambda kv: kv[1].get("date", ""), reverse=True))
        self._link()
        self._link_posts()

    # ---------- loading ----------
    def _load_region(self, slug, base):
        r = _read(base / "region.json")
        r["slug"] = slug
        pal = LANDS[slug]
        r.update(pal)
        r["pigment"], r["deep"] = pal["accent"], pal["ink"]
        r["url"] = reverse("region", args=[slug])
        r["places"], r["journeys"], r["stays"], r["guides"], r["festivals"], r["routes"] = [], [], [], [], [], []
        self.regions[slug] = r
        for p in sorted((base / "places").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("place", args=[slug, d["slug"]])
            self.places[d["slug"]] = d
            r["places"].append(d)
            for e in d.get("experiences", []):
                e["place"] = d["slug"]
                e["region"] = slug
                e["url"] = reverse("experience", args=[slug, d["slug"], e["slug"]])
                self.experiences[e["slug"]] = e
        for p in sorted((base / "journeys").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("journey", args=[d["slug"]])
            self.journeys[d["slug"]] = d
            r["journeys"].append(d)
        for name, store, key, view in (("stays.json", self.stays, "stays", "stay"),
                                       ("festivals.json", self.festivals, "festivals", "festival"),
                                       ("routes.json", self.routes, "routes", "route")):
            f = base / name
            for d in (_read(f) if f.exists() else []):
                d["region"] = slug
                d["url"] = reverse(view, args=[d["slug"]])
                store[d["slug"]] = d
                r[key].append(d)
        for p in sorted((base / "guides").glob("*.json")):
            d = _read(p)
            d["region"] = slug
            d["url"] = reverse("guide", args=[d["slug"]])
            self.guides[d["slug"]] = d
            r["guides"].append(d)

    def _imgs(self, *keys):
        for k in keys:
            if self.images.get(k):
                return self.images[k]
        return []

    def _link(self):
        # drop routes whose places do not exist (yet)
        for slug in [s for s, rt in self.routes.items() if rt.get("from") not in self.places or rt.get("to") not in self.places]:
            dead = self.routes.pop(slug)
            self.regions[dead["region"]]["routes"].remove(dead)
        for r in self.regions.values():
            r["images"] = self._imgs(f"region:{r['slug']}") or [
                i for p in r["places"][:6] for i in self._imgs(f"place:{p['slug']}")[:1]]
            r["best_label"] = best_range(r.get("best_months"))
            r["bar"] = month_bar(r.get("best_months"))
        for p in self.places.values():
            p["region_obj"] = self.regions[p["region"]]
            p["images"] = self._imgs(f"place:{p['slug']}")
            p["best_label"] = best_range(p.get("best_months"))
            p["bar"] = month_bar(p.get("best_months"))
            p["nearby_objs"] = [self.places[s] for s in p.get("nearby", []) if s in self.places]
            p["stay_objs"] = [self.stays[s] for s in p.get("stays", []) if s in self.stays]
            p["journey_objs"] = [j for j in self.journeys.values()
                                 if any(s["place"] == p["slug"] for s in j.get("stops", []))]
            p["festival_objs"] = [f for f in self.festivals.values() if f.get("place") == p["slug"]]
            p["route_objs"] = [rt for rt in self.routes.values() if p["slug"] in (rt.get("from"), rt.get("to"))]
        for r in self.regions.values():
            # the places most journeys stop at lead menus and supply the land's lead photos
            r["top_places"] = sorted(r["places"], key=lambda p: (-len(p["journey_objs"]), p["name"]))
            r["images"] = self._imgs(f"region:{r['slug']}") or [
                i for p in r["top_places"][:6] for i in p["images"][:1]]
        for e in self.experiences.values():
            place = self.places[e["place"]]
            e["place_obj"] = place
            e["region_obj"] = place["region_obj"]
            e["images"] = self._imgs(f"exp:{e['slug']}") or place["images"][1:] or place["images"]
            e["themes"] = place.get("themes", [])
        for s in self.stays.values():
            place = self.places.get(s.get("place"))
            s["place_obj"] = place
            s["region_obj"] = self.regions[s["region"]]
            s["images"] = self._imgs(f"stay:{s['slug']}") or (place["images"] if place else [])
            s["journey_objs"] = [j for j in self.journeys.values() if s["slug"] in j.get("stays", [])]
        for j in self.journeys.values():
            j["region_obj"] = self.regions[j["region"]]
            stops = [dict(st, obj=self.places[st["place"]]) for st in j.get("stops", []) if st["place"] in self.places]
            j["stop_objs"] = stops
            j["images"] = self._imgs(f"journey:{j['slug']}") or [
                i for st in stops for i in st["obj"]["images"][:1]]
            j["stay_objs"] = [self.stays[s] for s in j.get("stays", []) if s in self.stays]
            j["best_label"] = best_range(j.get("best_months"))
            j["bar"] = month_bar(j.get("best_months"))
            j["days_count"] = j.get("nights", 0) + 1
            for d in j.get("days", []):
                d["place_obj"] = self.places.get(d.get("place"))
        for g in self.guides.values():
            g["region_obj"] = self.regions[g["region"]]
            rel = [self.places[s] for s in g.get("related_places", []) if s in self.places]
            g["related_objs"] = rel
            g["images"] = self._imgs(f"guide:{g['slug']}") or [i for p in rel for i in p["images"][:1]] or g["region_obj"]["images"]
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in g.get("sections", []))
            g["read_min"] = max(3, round(words / 220))
            for s in g.get("sections", []):
                s["anchor"] = re.sub(r"[^a-z0-9]+", "-", s.get("heading", "").lower()).strip("-")
        for f in self.festivals.values():
            place = self.places.get(f.get("place"))
            f["place_obj"] = place
            f["region_obj"] = self.regions[f["region"]]
            f["images"] = self._imgs(f"fest:{f['slug']}") or (place["images"] if place else [])
        for rt in self.routes.values():
            rt["from_obj"] = self.places.get(rt.get("from"))
            rt["to_obj"] = self.places.get(rt.get("to"))
            rt["region_obj"] = self.regions[rt["region"]]
            rt["images"] = (rt["to_obj"] or {}).get("images", []) + (rt["from_obj"] or {}).get("images", [])[:1]
        for t in self.themes.values():
            t["url"] = reverse("theme", args=[t["slug"]])
        # ---- Himalaya Hives extras: tiers, altitude profiles, cheapest months, field notes
        for j in self.journeys.values():
            j["tier"] = j.get("tier") if j.get("tier") in TIERS else "comfort"
            j["tier_obj"] = TIERS[j["tier"]]
            prof = []
            for d in j.get("days", []):
                po = d.get("place_obj")
                if po and isinstance(po.get("altitude_m"), (int, float)):
                    prof.append({"day": d.get("day"), "alt": int(po["altitude_m"]), "name": d.get("overnight") or po["name"]})
            j["profile"] = prof
            j["max_sleep_alt"] = max((x["alt"] for x in prof), default=0)
            n = j.get("nights") or 1
            j["per_night"] = int(round((j.get("price_from_inr") or 0) / n, -2))
        for r in self.regions.values():
            js = r["journeys"]
            r["tier_from"] = {t: min((j.get("price_from_inr") or 0 for j in js if j["tier"] == t), default=0) for t in TIERS}
            r["saver_from"] = r["tier_from"]["saver"]
            r["saver_journeys"] = sorted([j for j in js if j["tier"] == "saver"], key=lambda j: j.get("price_from_inr") or 0)
            alts = [p["altitude_m"] for p in r["places"] if isinstance(p.get("altitude_m"), (int, float))]
            r["min_alt"], r["max_alt"] = (int(min(alts)), int(max(alts))) if alts else (0, 0)
            ms = r.get("months") or []
            r["cheap_months"] = [MONTHS[i] for i, m in enumerate(ms[:12])
                                 if m.get("price_level") == "low" and (r.get("best_months") or [0] * 12)[i] >= 1]
            r["field_notes"] = [dict(f, place=p) for p in r["places"] for f in p.get("field_notes", [])]
            r["budget_rows"] = [dict(b, tier_obj=TIERS.get(b.get("tier"), {})) for b in r.get("budget", [])]
            r["stays_by_tier"] = [(t, [s for s in r["stays"] if s.get("tier") == t]) for t in ("budget", "mid", "luxury")]
        for p in self.places.values():
            a = p.get("altitude_m")
            p["alt_label"] = f"{int(a):,} m" if isinstance(a, (int, float)) else ""

    def _link_posts(self):
        from datetime import date
        for d in self.posts.values():
            d["region_objs"] = [self.regions[r] for r in d.get("regions", []) if r in self.regions]
            d["journey_objs"] = [self.journeys[j] for j in d.get("related_journeys", []) if j in self.journeys]
            d["place_objs"] = [self.places[x] for x in d.get("related_places", []) if x in self.places]
            d["images"] = (self._imgs(f"blog:{d['slug']}") or [i for x in d["place_objs"] for i in x["images"][:1]])
            words = sum(len(" ".join(s.get("paras", []) + s.get("list", [])).split()) for s in d.get("sections", []))
            d["read_min"] = max(3, round(words / 220))
            d["cat_slug"] = re.sub(r"[^a-z0-9]+", "-", d.get("category", "").lower()).strip("-")
            try:
                d["date_obj"] = date.fromisoformat(d.get("date", ""))
            except ValueError:
                d["date_obj"] = None
            land = d["region_objs"][0]["slug"] if d["region_objs"] else None
            d["land"] = land
            stores = {"journey": self.journeys, "place": self.places, "stay": self.stays, "guide": self.guides, "festival": self.festivals}
            for sec in d.get("sections", []):
                sec["anchor"] = re.sub(r"[^a-z0-9]+", "-", sec.get("heading", "").lower()).strip("-")
                objs = []
                for ln in sec.get("links", []):
                    o = stores.get(ln.get("type"), {}).get(ln.get("slug"))
                    if o:
                        objs.append({"type": ln["type"], "title": o.get("title") or o.get("name"), "url": o["url"],
                                     "img": (o.get("images") or [None])[0]})
                sec["link_objs"] = objs
        self.post_categories = OrderedDict()
        for d in self.posts.values():
            self.post_categories.setdefault(d["cat_slug"], {"slug": d["cat_slug"], "name": d.get("category"), "posts": []})["posts"].append(d)

    # ---------- queries ----------
    def theme_items(self, theme, region=None):
        def ok(x):
            return region is None or x.get("region") == region
        places = [p for p in self.places.values() if theme in p.get("themes", []) and ok(p)]
        journeys = [j for j in self.journeys.values() if theme in j.get("themes", []) and ok(j)]
        place_slugs = {p["slug"] for p in places}
        stays = [s for s in self.stays.values() if s.get("place") in place_slugs and ok(s)]
        experiences = [e for e in self.experiences.values() if e["place"] in place_slugs and ok(e)]
        return {"places": places, "journeys": journeys, "stays": stays, "experiences": experiences}

    def region_theme_pairs(self):
        """(region, theme) pairs with enough content to deserve a page."""
        out = []
        for r in self.regions:
            for t in self.themes:
                items = self.theme_items(t, r)
                if len(items["places"]) >= 2 and (items["journeys"] or len(items["places"]) >= 3):
                    out.append((r, t))
        return out

    def region_kind_pairs(self):
        """(region, kind) pairs with at least 3 experiences."""
        out = []
        for r in self.regions:
            for k in KINDS:
                if sum(1 for e in self.experiences.values() if e["region"] == r and e.get("kind") == k) >= 3:
                    out.append((r, k))
        return out

    def affordable(self, region=None, under=None):
        js = [j for j in self.journeys.values() if j["tier"] == "saver"
              and (region is None or j["region"] == region)
              and (under is None or (j.get("price_from_inr") or 0) <= under)]
        return sorted(js, key=lambda j: j.get("price_from_inr") or 0)

    def tier_journeys(self, tier):
        return sorted([j for j in self.journeys.values() if j["tier"] == tier],
                      key=lambda j: (REGION_ORDER.index(j["region"]), j.get("price_from_inr") or 0))

    def field_notes(self):
        return [f for r in self.regions.values() for f in r["field_notes"]]

    def counts(self):
        return {
            "regions": len(self.regions), "places": len(self.places), "experiences": len(self.experiences),
            "journeys": len(self.journeys), "stays": len(self.stays), "guides": len(self.guides),
            "festivals": len(self.festivals), "routes": len(self.routes), "themes": len(self.themes),
            "posts": len(self.posts),
        }

    def all_images(self):
        seen, out = set(), []
        for key, recs in self.images.items():
            for rec in recs:
                if rec["file"] not in seen:
                    seen.add(rec["file"])
                    out.append(dict(rec, used_for=key))
        return out
