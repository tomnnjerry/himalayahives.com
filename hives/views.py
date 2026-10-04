import json
from datetime import date

from django.conf import settings
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .content import KINDS, MONTH_SHORT, MONTHS, REGION_ORDER, TIERS, catalogue, month_bar
from .forms import EnquiryForm, SubscribeForm
from .models import Subscriber
from .policies import POLICIES, UPDATED

COMPANY_FAQS = [
    {"q": "What does Himalaya Hives do?",
     "a": "We plan trips in the Himalaya and nowhere else: Kashmir, Ladakh, Himachal, Spiti and Lahaul, Garhwal, Kumaon, Nepal, Darjeeling and Kalimpong, Sikkim, Bhutan and Arunachal. Every trip comes in three tiers, Saver, Comfort and Signature, so you choose how you travel and what you spend."},
    {"q": "What is a Saver trip?",
     "a": "Saver trips are our affordable Himalaya: state buses and shared jeeps where they run reliably, homestays, hostels and government tourist bungalows, and local food. They are planned and supported like every other trip, with honest notes on comfort, bathrooms and road times."},
    {"q": "Are your prices fixed?",
     "a": "No. Prices on the site are indicative 'from' prices in INR per person, twin sharing, for 2026. The final price depends on dates, rooms and availability. We send a written quote with every line itemised before you pay anything."},
    {"q": "Can you change a trip on the site?",
     "a": "Yes. The trips on the site show what works on each route. We change hotels, add nights, swap tiers for part of the trip and combine hives, then send a new day-by-day plan."},
    {"q": "How do you handle altitude?",
     "a": "Every trip page shows a sleeping-altitude profile. Above 3,000 m we follow the usual advice of gaining no more than 300 to 500 m of sleeping height a day, with rest days. We are not doctors: talk to yours before any trip above 3,000 m, especially with heart or lung conditions."},
    {"q": "Who will we deal with?",
     "a": "One planner handles your trip from the first message to the last transfer and is reachable on WhatsApp while you travel. On the ground we work with local drivers, guides and homestay families on routes they know."},
    {"q": "Where do your photos and facts come from?",
     "a": "Every photo comes from Wikimedia Commons under a free licence, credited under the photo and on our photo credits page. Every field note names its source, usually a Wikipedia article or a public body, so you can check it."},
    {"q": "Do you arrange permits?",
     "a": "Yes, where a registered agent can apply: Inner Line Permits, Protected Area Permits, Bhutan entry permits and trekking permits in Nepal. Rules change often, so we send current guidance with your quote. Check current status before you travel."},
    {"q": "Is travel insurance included?",
     "a": "No. We ask every traveller to hold insurance that covers medical evacuation and the highest altitude on the route. For treks above 4,000 m and adventure sports, check that your policy names them."},
]


def ld(*items):
    """Render JSON-LD blocks safely."""
    return [json.dumps(i, ensure_ascii=False).replace("</", "<\\/") for i in items]


def crumbs(*pairs):
    items = [("Home", reverse("home"))] + list(pairs)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": settings.SITE["url"] + u}
        for i, (n, u) in enumerate(items)]}
    return items, data


def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faqs]}


def img_url(obj):
    imgs = obj.get("images") or []
    return imgs[0]["thumb"] if imgs else None


def org_ld():
    s = settings.SITE
    return {"@context": "https://schema.org", "@type": "TravelAgency", "name": s["name"], "url": s["url"],
            "areaServed": ["Jammu and Kashmir", "Ladakh", "Himachal Pradesh", "Uttarakhand", "Nepal", "West Bengal", "Sikkim", "Bhutan", "Arunachal Pradesh"],
            "slogan": "Every valley is a hive"}


def _get(store, slug):
    obj = store.get(slug)
    if not obj:
        raise Http404
    return obj


def _month_now():
    return date.today().month - 1


# ---------------- home and indexes ----------------
def home(request):
    from .content import BUDGET_BANDS, TIERS
    from .terrain import arc_svg
    cat = catalogue()
    regions = list(cat.regions.values())
    featured = []
    for r in regions:  # one comfort trip per hive, topped up to a full row of four
        cj = [j for j in r["journeys"] if j["tier"] == "comfort"] or r["journeys"]
        if cj:
            featured.append(sorted(cj, key=lambda j: j.get("price_from_inr", 0))[len(cj) // 2])
    featured = featured[: (len(featured) // 4) * 4 or len(featured)]
    m = _month_now()
    in_season = [p for p in cat.places.values() if (p.get("best_months") or [0] * 12)[m] == 2]
    in_season = sorted(in_season, key=lambda p: REGION_ORDER.index(p["region"]))[::max(1, len(in_season) // 8)][:8]
    fests = [f for f in cat.festivals.values() if (m + 1) in f.get("month_nums", []) or ((m + 1) % 12 + 1) in f.get("month_nums", [])][:4]
    tiers = []
    for t, info in TIERS.items():
        js = cat.tier_journeys(t)
        tiers.append({"slug": t, **info, "from": min((j["price_from_inr"] for j in js), default=0),
                      "per_day": [b["per_day_inr"] for r in regions for b in r.get("budget", []) if b.get("tier") == t][:1],
                      "examples": js[::max(1, len(js) // 3)][:3]})
    savers = cat.affordable()
    bands = [{"amount": a, "label": l, "trips": [j for j in savers if j["price_from_inr"] <= a][:4]} for a, l in BUDGET_BANDS]
    notes = cat.field_notes()
    day = date.today().toordinal()
    notes = [notes[(day * 7 + i * 37) % len(notes)] for i in range(6)] if notes else []
    words = [dict(g, region=r) for r in regions for g in r.get("glossary", [])[:2]]
    arc, arc_pts = arc_svg(regions) if regions else ("", [])
    almanac = [{"r": r, "cells": [{"v": (r.get("best_months") or [0] * 12)[i],
                                   "price": ((r.get("months") or [{}] * 12)[i] if i < len(r.get("months") or []) else {}).get("price_level", ""),
                                   "m": MONTHS[i]} for i in range(12)]} for r in regions]
    return render(request, "hives/home.html", {
        "regions": regions, "featured": featured[:8], "month": MONTHS[m], "month_i": m,
        "in_season": in_season, "festivals": fests, "guides": list(cat.guides.values())[::9][:3],
        "themes": list(cat.themes.values()), "months_short": MONTH_SHORT, "months_full": MONTHS,
        "posts": list(cat.posts.values())[:3], "tiers": tiers, "bands": bands, "notes": notes, "words": words,
        "arc": arc, "arc_pts": arc_pts, "almanac": almanac, "saver_from": min((j["price_from_inr"] for j in savers), default=0),
        "ld": ld(org_ld(), {"@context": "https://schema.org", "@type": "WebSite", "name": settings.SITE["name"], "url": settings.SITE["url"],
                            "potentialAction": {"@type": "SearchAction", "target": settings.SITE["url"] + "/?q={q}", "query-input": "required name=q"}}),
    })


def lands(request):
    cat = catalogue()
    items, bc = crumbs(("Hives", reverse("lands")))
    return render(request, "hives/lands.html", {"regions": list(cat.regions.values()), "crumbs": items,
                                                "months_short": MONTH_SHORT, "ld": ld(bc)})


def region(request, region):
    cat = catalogue()
    r = _get(cat.regions, region)
    items, bc = crumbs(("Hives", reverse("lands")), (r["name"], r["url"]))
    exps = [e for p in r["places"] for e in p.get("experiences", [])[:1]]
    styles = [cat.themes[t] for (rr, t) in cat.region_theme_pairs() if rr == region]
    rm = r.get("months") or []
    months = [{"name": MONTHS[i], "slug": MONTHS[i].lower(), "rating": (r.get("best_months") or [0] * 12)[i],
               "weather": rm[i].get("weather", "") if i < len(rm) else "",
               "price": rm[i].get("price_level", "") if i < len(rm) else "",
               "crowd": rm[i].get("crowd", "") if i < len(rm) else ""} for i in range(12)]
    place_ld = {"@context": "https://schema.org", "@type": "TouristDestination", "name": r["name"],
                "description": r.get("summary"), "url": settings.SITE["url"] + r["url"],
                "includesAttraction": [{"@type": "TouristAttraction", "name": p["name"]} for p in r["places"]]}
    tier_groups = [{"slug": t, **TIERS[t], "journeys": sorted([j for j in r["journeys"] if j["tier"] == t],
                                                              key=lambda j: j.get("price_from_inr") or 0)} for t in TIERS]
    return render(request, "hives/region.html", {
        "r": r, "crumbs": items, "experiences": exps, "styles": styles, "months": months, "tier_groups": tier_groups,
        "kinds": [(k, KINDS[k][0]) for rr, k in cat.region_kind_pairs() if rr == region],
        "ld": ld(bc, place_ld, faq_ld(r.get("faqs", []))),
        "map_points": json.dumps([{"name": p["name"], "lat": p.get("lat"), "lng": p.get("lng"), "url": p["url"],
                                   "kind": p.get("kind", "")} for p in r["places"] if p.get("lat")]),
    })


def region_month(request, region, month):
    cat = catalogue()
    r = _get(cat.regions, region)
    names = [m.lower() for m in MONTHS]
    if month not in names:
        raise Http404
    i = names.index(month)
    md = r.get("months", [])[i] if i < len(r.get("months", [])) else {}
    go = [cat.places[s] for s in md.get("go", []) if s in cat.places]
    events = [cat.festivals[s] for s in md.get("events", []) if s in cat.festivals]
    journeys = [j for j in r["journeys"] if (j.get("best_months") or [0] * 12)[i] == 2]
    rating = (r.get("best_months") or [0] * 12)[i]
    others = [{"r": rr, "rating": (rr.get("best_months") or [0] * 12)[i]} for rr in cat.regions.values() if rr["slug"] != region]
    items, bc = crumbs(("Hives", reverse("lands")), (r["name"], r["url"]), (f"{MONTHS[i]}", request.path))
    title = f"{r['name']} in {MONTHS[i]}"
    faqs = [
        {"q": f"Is {MONTHS[i]} a good time to visit {r['name']}?",
         "a": (md.get("summary") or "")[:600] or f"See our month-by-month notes for {r['name']}."},
        {"q": f"What is the weather like in {r['name']} in {MONTHS[i]}?",
         "a": f"{md.get('weather', 'Weather varies across the region')}. Conditions differ by altitude and coast, so check the forecast for each stop a week before you travel."},
        {"q": f"Where should we go in {r['name']} in {MONTHS[i]}?",
         "a": (("We suggest " + ", ".join(p["name"] for p in go) + ". " if go else "") + (md.get("tip") or "")).strip()
              or f"Tell us your dates and budget and we will suggest the parts of {r['name']} that work best in {MONTHS[i]}."},
    ]
    return render(request, "hives/region_month.html", {
        "r": r, "i": i, "month": MONTHS[i], "md": md, "go": go, "events": events, "journeys": journeys,
        "rating": rating, "others": others, "crumbs": items, "title": title, "faqs": faqs,
        "prev": names[(i - 1) % 12], "next": names[(i + 1) % 12], "prev_name": MONTHS[(i - 1) % 12], "next_name": MONTHS[(i + 1) % 12],
        "ld": ld(bc, faq_ld(faqs)),
    })


def region_theme(request, region, theme):
    cat = catalogue()
    r = _get(cat.regions, region)
    t = _get(cat.themes, theme)
    if (region, theme) not in cat.region_theme_pairs():
        raise Http404
    data = cat.theme_items(theme, region)
    items, bc = crumbs(("Hives", reverse("lands")), (r["name"], r["url"]), (t["name"], request.path))
    return render(request, "hives/region_theme.html", {"r": r, "t": t, **data, "crumbs": items, "ld": ld(bc)})


def place(request, region, place):
    cat = catalogue()
    p = _get(cat.places, place)
    if p["region"] != region:
        return redirect(p["url"], permanent=True)
    r = p["region_obj"]
    items, bc = crumbs(("Hives", reverse("lands")), (r["name"], r["url"]), (p["name"], p["url"]))
    dest = {"@context": "https://schema.org", "@type": "TouristDestination", "name": p["name"],
            "description": p.get("summary"), "url": settings.SITE["url"] + p["url"], "image": img_url(p)}
    if p.get("lat"):
        dest["geo"] = {"@type": "GeoCoordinates", "latitude": p["lat"], "longitude": p["lng"]}
    return render(request, "hives/place.html", {
        "p": p, "r": r, "crumbs": items, "ld": ld(bc, dest, faq_ld(p.get("faqs", []))),
        "map_points": json.dumps([{"name": x["name"], "lat": x.get("lat"), "lng": x.get("lng"), "url": x["url"], "main": x is p}
                                  for x in [p] + p["nearby_objs"] if x.get("lat")]),
    })


def experience(request, region, place, exp):
    cat = catalogue()
    e = _get(cat.experiences, exp)
    p = e["place_obj"]
    if p["slug"] != place or e["region"] != region:
        return redirect(e["url"], permanent=True)
    r = e["region_obj"]
    siblings = [x for x in p.get("experiences", []) if x is not e]
    items, bc = crumbs(("Hives", reverse("lands")), (r["name"], r["url"]), (p["name"], p["url"]), (e["title"], e["url"]))
    attraction = {"@context": "https://schema.org", "@type": "TouristAttraction", "name": e["title"],
                  "description": e.get("summary"), "image": img_url(e),
                  "containedInPlace": {"@type": "Place", "name": p["name"]}}
    return render(request, "hives/experience.html", {
        "e": e, "p": p, "r": r, "siblings": siblings, "crumbs": items,
        "ld": ld(bc, attraction, faq_ld(e.get("faqs", []))),
    })


def journeys(request):
    cat = catalogue()
    items, bc = crumbs(("Trips", reverse("journeys")))
    return render(request, "hives/journeys.html", {"journeys": list(cat.journeys.values()), "regions": list(cat.regions.values()),
                                                   "themes": list(cat.themes.values()), "crumbs": items, "ld": ld(bc)})


def journey(request, slug):
    cat = catalogue()
    j = _get(cat.journeys, slug)
    r = j["region_obj"]
    items, bc = crumbs(("Trips", reverse("journeys")), (j["title"], j["url"]))
    trip = {"@context": "https://schema.org", "@type": "TouristTrip", "name": j["title"], "description": j.get("summary"),
            "image": img_url(j), "touristType": [cat.themes[t]["name"] for t in j.get("themes", []) if t in cat.themes],
            "itinerary": {"@type": "ItemList", "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "item": {"@type": "Place", "name": s["obj"]["name"]}}
                for i, s in enumerate(j["stop_objs"])]},
            "offers": {"@type": "Offer", "priceCurrency": "INR", "price": j.get("price_from_inr"),
                       "description": "Indicative price per person, twin sharing"}}
    related = ([x for x in r["journeys"] if x is not j and x["tier"] != j["tier"]][:2] +
               [x for x in r["journeys"] if x is not j and x["tier"] == j["tier"]])[:3]
    same_route = [x for x in r["journeys"] if x is not j and x["tier"] != j["tier"]
                  and {s["place"] for s in x.get("stops", [])} & {s["place"] for s in j.get("stops", [])}][:2]
    return render(request, "hives/journey.html", {
        "j": j, "r": r, "crumbs": items, "related": related, "same_route": same_route,
        "ld": ld(bc, trip, faq_ld(j.get("faqs", []))),
        "map_points": json.dumps([{"name": s["obj"]["name"], "lat": s["obj"].get("lat"), "lng": s["obj"].get("lng"),
                                   "url": s["obj"]["url"], "nights": s["nights"]} for s in j["stop_objs"] if s["obj"].get("lat")]),
    })


def stays(request):
    cat = catalogue()
    items, bc = crumbs(("Stays", reverse("stays")))
    return render(request, "hives/stays.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def stay(request, slug):
    cat = catalogue()
    s = _get(cat.stays, slug)
    items, bc = crumbs(("Stays", reverse("stays")), (s["name"], s["url"]))
    hotel = {"@context": "https://schema.org", "@type": "Hotel", "name": s["name"], "description": s.get("summary"),
             "image": img_url(s), "address": {"@type": "PostalAddress", "addressLocality": (s.get("place_obj") or {}).get("name", "")}}
    if s.get("website"):
        hotel["sameAs"] = s["website"]
    others = [x for x in s["region_obj"]["stays"] if x is not s][:3]
    return render(request, "hives/stay.html", {"s": s, "crumbs": items, "others": others,
                                               "ld": ld(bc, hotel, faq_ld(s.get("faqs", [])))})


def experiences(request):
    cat = catalogue()
    items, bc = crumbs(("Experiences", reverse("experiences")))
    kinds = sorted({e.get("kind", "") for e in cat.experiences.values() if e.get("kind")})
    return render(request, "hives/experiences.html", {"regions": list(cat.regions.values()), "kinds": kinds,
                                                      "kind_links": [(k, v[0]) for k, v in KINDS.items()],
                                                      "count": len(cat.experiences), "crumbs": items, "ld": ld(bc)})


def _kind_page(request, kind, region=None):
    cat = catalogue()
    if kind not in KINDS:
        raise Http404
    name, tagline, intro = KINDS[kind]
    exps = [e for e in cat.experiences.values() if e.get("kind") == kind and (region is None or e["region"] == region)]
    r = cat.regions.get(region) if region else None
    if region and (not r or (region, kind) not in cat.region_kind_pairs()):
        raise Http404
    trail = [("Experiences", reverse("experiences"))]
    if r:
        trail = [("Hives", reverse("lands")), (r["name"], r["url"]), (f"{name} experiences", request.path)]
    else:
        trail.append((name, request.path))
    items, bc = crumbs(*trail)
    lands = [cat.regions[rr] for rr, k in cat.region_kind_pairs() if k == kind]
    others = [(k, v[0]) for k, v in KINDS.items() if k != kind and (region is None or (region, k) in cat.region_kind_pairs())]
    return render(request, "hives/experience_kind.html", {
        "kind": kind, "name": name, "tagline": tagline, "intro": intro, "exps": exps, "r": r,
        "lands": lands, "others": others, "crumbs": items, "ld": ld(bc)})


def experience_kind(request, kind):
    return _kind_page(request, kind)


def region_kind(request, region, kind):
    return _kind_page(request, kind, region)


def guides(request):
    cat = catalogue()
    items, bc = crumbs(("Guides", reverse("guides")))
    return render(request, "hives/guides.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def guide(request, slug):
    cat = catalogue()
    g = _get(cat.guides, slug)
    r = g["region_obj"]
    items, bc = crumbs(("Guides", reverse("guides")), (g["title"], g["url"]))
    article = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g.get("summary"),
               "image": img_url(g), "author": {"@type": "Organization", "name": settings.SITE["byline"]},
               "publisher": {"@type": "Organization", "name": settings.SITE["name"]}}
    more = [x for x in r["guides"] if x is not g][:3]
    return render(request, "hives/guide.html", {"g": g, "r": r, "crumbs": items, "more": more,
                                                "ld": ld(bc, article, faq_ld(g.get("faqs", [])))})


def festivals(request):
    cat = catalogue()
    items, bc = crumbs(("Festivals", reverse("festivals")))
    by_month = []
    for i, m in enumerate(MONTHS):
        fs = [f for f in cat.festivals.values() if (i + 1) in f.get("month_nums", [])]
        by_month.append({"name": m, "festivals": fs})
    return render(request, "hives/festivals.html", {"by_month": by_month, "count": len(cat.festivals), "crumbs": items, "ld": ld(bc)})


def festival(request, slug):
    cat = catalogue()
    f = _get(cat.festivals, slug)
    items, bc = crumbs(("Festivals", reverse("festivals")), (f["name"], f["url"]))
    journeys = [j for j in f["region_obj"]["journeys"] if "festivals" in j.get("themes", [])][:3]
    return render(request, "hives/festival.html", {"f": f, "crumbs": items, "journeys": journeys,
                                                   "bar": month_bar([2 if (i + 1) in f.get("month_nums", []) else 0 for i in range(12)]),
                                                   "ld": ld(bc, faq_ld(f.get("faqs", [])))})


def routes(request):
    cat = catalogue()
    items, bc = crumbs(("Routes", reverse("routes")))
    return render(request, "hives/routes.html", {"regions": list(cat.regions.values()), "crumbs": items, "ld": ld(bc)})


def route(request, slug):
    cat = catalogue()
    rt = _get(cat.routes, slug)
    if not (rt["from_obj"] and rt["to_obj"]):
        raise Http404
    items, bc = crumbs(("Routes", reverse("routes")), (f"{rt['from_obj']['name']} to {rt['to_obj']['name']}", rt["url"]))
    pts = [x for x in (rt["from_obj"], rt["to_obj"]) if x and x.get("lat")]
    return render(request, "hives/route.html", {"rt": rt, "crumbs": items, "ld": ld(bc, faq_ld(rt.get("faqs", []))),
                                                "map_points": json.dumps([{"name": x["name"], "lat": x["lat"], "lng": x["lng"], "url": x["url"]} for x in pts])})


def themes(request):
    cat = catalogue()
    items, bc = crumbs(("Styles", reverse("themes")))
    rows = [{"t": t, "n": len(cat.theme_items(t["slug"])["journeys"])} for t in cat.themes.values()]
    return render(request, "hives/themes.html", {"rows": rows, "crumbs": items, "ld": ld(bc)})


def theme(request, slug):
    cat = catalogue()
    t = _get(cat.themes, slug)
    data = cat.theme_items(slug)
    pairs = [cat.regions[r] for (r, tt) in cat.region_theme_pairs() if tt == slug]
    items, bc = crumbs(("Styles", reverse("themes")), (t["name"], t["url"]))
    return render(request, "hives/theme.html", {"t": t, **data, "region_pages": pairs, "crumbs": items, "ld": ld(bc)})


def seasons(request):
    cat = catalogue()
    items, bc = crumbs(("Seasons", reverse("seasons")))
    return render(request, "hives/seasons.html", {"regions": list(cat.regions.values()), "months": MONTHS,
                                                  "months_short": MONTH_SHORT, "crumbs": items, "ld": ld(bc)})


# ---------------- tools ----------------
def tools(request):
    items, bc = crumbs(("Trip tools", reverse("tools")))
    return render(request, "hives/tools.html", {"crumbs": items, "ld": ld(bc)})


def tool_season(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Season finder", reverse("tool_season")))
    data = [{"n": p["name"], "u": p["url"], "r": p["region_obj"]["name"], "rs": p["region"], "b": p.get("best_months") or [0] * 12,
             "k": p.get("kind", ""), "i": (p["images"][0]["thumb"] if p["images"] else "")} for p in cat.places.values()]
    return render(request, "hives/tool_season.html", {"crumbs": items, "data": json.dumps(data).replace("</", "<\\/"), "months": MONTHS, "ld": ld(bc),
                                                      "regions": list(cat.regions.values()), "now": _month_now()})


def tool_budget(request):
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Budget builder", reverse("tool_budget")))
    return render(request, "hives/tool_budget.html", {"crumbs": items, "ld": ld(bc), "regions": list(catalogue().regions.values())})


def tool_permits(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Permits", reverse("tool_permits")))
    return render(request, "hives/tool_permits.html", {"crumbs": items, "ld": ld(bc), "regions": list(cat.regions.values())})


# ---------------- enquiry ----------------
def _notify(e):
    """Email the planners about a new enquiry when HH_NOTIFY_EMAIL is set. Never blocks the visitor."""
    to = getattr(settings, "HH_NOTIFY_EMAIL", "")
    if not to:
        return
    from django.core.mail import send_mail
    lines = [f"{k}: {v}" for k, v in (("Name", e.name), ("Email", e.email), ("Phone", e.phone), ("Prefers", e.contact_pref),
                                      ("Hives", e.lands), ("Month", e.month), ("Nights", e.nights), ("Travellers", e.travellers),
                                      ("Budget", e.budget), ("Form", e.kind), ("Page", e.source_page)) if v]
    try:
        send_mail(f"New enquiry: {e.name} ({e.lands or 'any hive'})", "\n".join(lines) + "\n\n" + (e.message or ""),
                  None, [to], fail_silently=True)
    except Exception:  # noqa: BLE001
        pass


def plan(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save()
            _notify(enquiry)
            return redirect("plan_thanks")
    else:
        initial = {"source_page": request.GET.get("from", "")[:300], "kind": "full"}
        if request.GET.get("land"):
            initial["lands"] = [request.GET["land"]]
        if request.GET.get("month") in MONTHS:
            initial["month"] = request.GET["month"]
        if request.GET.get("journey"):
            initial["message"] = f"I am interested in: {request.GET['journey'][:150]}"
        form = EnquiryForm(initial=initial)
    items, bc = crumbs(("Plan a journey", reverse("plan")))
    return render(request, "hives/plan.html", {"form": form, "crumbs": items, "ld": ld(bc)})


def plan_thanks(request):
    return render(request, "hives/plan_thanks.html", {"crumbs": crumbs(("Plan a journey", reverse("plan")))[0]})


# ---------------- static and utility ----------------
def old_policy(request, page):
    return redirect("policy", slug={"privacy": "privacy", "terms": "booking-terms"}[page], permanent=True)


def static_page(request, page):
    titles = {"about": "About us", "privacy": "Privacy", "terms": "Terms"}
    items, bc = crumbs((titles[page], request.path))
    return render(request, f"hives/{page}.html", {"crumbs": items, "counts": catalogue().counts(), "ld": ld(bc)})


def faq(request):
    cat = catalogue()
    items, bc = crumbs(("FAQ", reverse("faq")))
    groups = [{"name": "Travelling with us", "faqs": COMPANY_FAQS}] + [
        {"name": r["name"], "faqs": r.get("faqs", []), "url": r["url"]} for r in cat.regions.values()]
    return render(request, "hives/faq.html", {"groups": groups, "crumbs": items, "ld": ld(bc, faq_ld(COMPANY_FAQS))})


def photo_credits(request):
    cat = catalogue()
    items, bc = crumbs(("Photo credits", reverse("photo_credits")))
    return render(request, "hives/photo_credits.html", {"images": cat.all_images(), "crumbs": items, "ld": ld(bc)})


def html_sitemap(request):
    cat = catalogue()
    items, bc = crumbs(("Sitemap", reverse("html_sitemap")))
    return render(request, "hives/sitemap.html", {"cat": cat, "regions": list(cat.regions.values()), "crumbs": items,
                                                  "pairs": [(cat.regions[r], cat.themes[t]) for r, t in cat.region_theme_pairs()],
                                                  "kind_pairs": [(cat.regions[r], k, KINDS[k][0]) for r, k in cat.region_kind_pairs()],
                                                  "month_slugs": [(m, m.lower()) for m in MONTHS], "ld": ld(bc)})


def robots(request):
    body = f"User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /plan/thank-you/\n\nSitemap: {settings.SITE['url']}/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain")


def llms(request):
    cat = catalogue()
    lines = [f"# {settings.SITE['name']}", "",
             "> Himalaya-only trip planner. Eleven hives from Kashmir to Arunachal, each trip in Saver, Comfort and Signature tiers with indicative INR prices, altitude profiles and sourced local facts.", ""]
    for r in cat.regions.values():
        lines.append(f"## {r['name']}")
        lines.append(f"- [{r['name']} overview]({settings.SITE['url']}{r['url']}): {r.get('summary', '')}")
        for p in r["places"]:
            lines.append(f"- [{p['name']}]({settings.SITE['url']}{p['url']}): {p.get('summary', '')}")
        for j in r["journeys"]:
            lines.append(f"- [{j['title']}]({settings.SITE['url']}{j['url']}) ({j['tier_obj']['name']}, {j['nights']} nights, from INR {j.get('price_from_inr')} pp): {j.get('summary', '')}")
        lines.append("")
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def not_found(request, exception=None):
    return render(request, "hives/404.html", {"crumbs": []}, status=404)
