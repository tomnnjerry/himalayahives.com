"""Himalaya Hives pages: the affordable section, price tiers, field notes, altitude tool, design system."""
import json

from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from .content import BUDGET_BANDS, MONTHS, TIERS, catalogue
from .views import _get, crumbs, faq_ld, ld

AFFORDABLE_FAQS = [
    {"q": "What is the cheapest way to travel in the Himalaya?",
     "a": "State buses and shared jeeps, homestays and government tourist bungalows, and travelling in the shoulder months. A Saver day in most Indian hives costs about ₹2,000–4,000 per person for bed, food and local transport (indicative 2026). Overland Nepal and Bhutan by road are often cheaper than flying in."},
    {"q": "Are Saver trips safe?",
     "a": "Yes, when they are planned well. We use routes where state buses and shared jeeps run every day in season, registered homestays and rest houses, and we keep a planner on WhatsApp throughout. Saver trips keep the same altitude rules and spare days as our other tiers."},
    {"q": "What do Saver trips leave out?",
     "a": "Private transport, hotel comforts and sometimes an attached bathroom. In the high valleys a homestay may have a shared or outside toilet and hot water by the bucket. Each trip page says plainly what to expect."},
    {"q": "Which hive is cheapest?",
     "a": "Spiti, Kumaon, Darjeeling and Nepal tend to be the easiest on a small budget, because buses, shared taxis and homestays are common. Bhutan and Ladakh cost more: Bhutan because of its daily Sustainable Development Fee, Ladakh because of flights and permits. Check current status before you travel."},
    {"q": "When is the cheapest time to go?",
     "a": "The shoulder months either side of each hive's peak: late March and April, and October into November in most of the range. Rooms are cheaper, buses are less full and the weather is usually settled. Each hive page marks its low-price months."},
    {"q": "Do Saver prices include travel to the start?",
     "a": "No. Saver prices start at the trip's start point, such as Shimla, Manali, Siliguri or Kathgodam. We suggest the cheapest way to get there, usually an overnight train or Volvo bus, and can book it for you."},
]


def _bands():
    return [{"amount": a, "label": l, "url": reverse("affordable_under", args=[a])} for a, l in BUDGET_BANDS]


def affordable(request):
    cat = catalogue()
    regions = list(cat.regions.values())
    savers = cat.affordable()
    items, bc = crumbs(("Affordable Himalaya", reverse("affordable")))
    rows = []
    for r in regions:
        saver = [b for b in r.get("budget", []) if b.get("tier") == "saver"]
        rows.append({"r": r, "per_day": saver[0]["per_day_inr"] if saver else "", "from": r["saver_from"],
                     "cheap": r["cheap_months"][:4], "tip": (r.get("money_savers") or [""])[0]})
    budget_stays = [s for s in cat.stays.values() if s.get("tier") == "budget"]
    return render(request, "hives/affordable.html", {
        "savers": savers, "rows": rows, "bands": _bands(), "budget_stays": budget_stays[::max(1, len(budget_stays) // 8)][:8],
        "faqs": AFFORDABLE_FAQS, "crumbs": items, "ld": ld(bc, faq_ld(AFFORDABLE_FAQS)),
        "guides": [g for g in cat.guides.values() if g.get("category") == "budget"][:6],
    })


def affordable_under(request, amount):
    cat = catalogue()
    bands = dict(BUDGET_BANDS)
    if amount not in bands:
        raise Http404
    trips = cat.affordable(under=amount)
    items, bc = crumbs(("Affordable Himalaya", reverse("affordable")), (f"Trips {bands[amount].lower()}", request.path))
    faqs = [
        {"q": f"Can you travel in the Himalaya {bands[amount].lower()}?",
         "a": f"Yes. These Saver trips start at or below ₹{amount:,} per person, twin sharing, from the trip's start point (indicative 2026). They use state buses or shared jeeps, homestays and simple hotels. Travel to the start point is extra; an overnight train or bus keeps that cheap too."},
        {"q": "What is not included at this price?",
         "a": "Travel to the start point, lunches on most days, entry fees, tips and anything private. Each trip lists its own inclusions and exclusions. Prices rise in peak weeks and festival dates, so check the dates you have in mind with us."},
        {"q": "Can we upgrade part of a Saver trip?",
         "a": "Yes. Many travellers keep buses and homestays for most of the trip and add a private car for one long day, or a better hotel for the last night. We price each change line by line."},
    ]
    return render(request, "hives/affordable_list.html", {
        "trips": trips, "amount": amount, "label": bands[amount], "bands": _bands(), "faqs": faqs,
        "crumbs": items, "ld": ld(bc, faq_ld(faqs)), "regions": list(cat.regions.values())})


def affordable_region(request, region):
    cat = catalogue()
    r = _get(cat.regions, region)
    items, bc = crumbs(("Affordable Himalaya", reverse("affordable")), (f"{r['name']} on a budget", request.path))
    costs = [dict(row=c, place=p) for p in r["places"] for c in p.get("costs", [])[:2]]
    stays = [s for s in r["stays"] if s.get("tier") == "budget"]
    guides = [g for g in r["guides"] if g.get("category") == "budget"] or r["guides"][:1]
    rm = r.get("months") or []
    months = [{"m": MONTHS[i], "price": rm[i].get("price_level", "") if i < len(rm) else "",
               "rating": (r.get("best_months") or [0] * 12)[i]} for i in range(12)]
    saver = next((b for b in r.get("budget", []) if b.get("tier") == "saver"), {})
    faqs = [
        {"q": f"How much does a budget trip to {r['name']} cost?",
         "a": f"A Saver day in {r['name']} costs about ₹{saver.get('per_day_inr', '—')} per person ({saver.get('covers', 'bed, food and local transport')}). Our Saver trips here start from ₹{r['saver_from']:,} per person, twin sharing, indicative 2026, from the start point."},
        {"q": f"What is the cheapest month for {r['name']}?",
         "a": (f"Rooms and transport are cheapest in {', '.join(r['cheap_months'][:3])}, when the weather still works for most of the hive. " if r["cheap_months"] else "")
              + "Peak weeks, school holidays and festival dates cost more. Check current status before you travel."},
        {"q": f"How do we save money in {r['name']}?",
         "a": " ".join((r.get("money_savers") or [])[:3])},
    ]
    return render(request, "hives/affordable_region.html", {
        "r": r, "costs": costs, "stays": stays, "guides": guides, "months": months, "saver": saver, "faqs": faqs,
        "bands": _bands(), "crumbs": items, "ld": ld(bc, faq_ld(faqs))})


def tier(request, tier):
    cat = catalogue()
    if tier not in TIERS:
        raise Http404
    t = TIERS[tier]
    trips = cat.tier_journeys(tier)
    items, bc = crumbs(("Trips", reverse("journeys")), (f"{t['name']} trips", request.path))
    rows = [{"r": r, "budget": next((b for b in r.get("budget", []) if b.get("tier") == tier), {}),
             "from": r["tier_from"].get(tier)} for r in cat.regions.values()]
    return render(request, "hives/tier.html", {"t": dict(t, slug=tier), "trips": trips, "rows": rows,
                                               "tiers": [dict(v, slug=k) for k, v in TIERS.items()],
                                               "crumbs": items, "ld": ld(bc)})


def field_notes(request):
    cat = catalogue()
    items, bc = crumbs(("Field notes", reverse("field_notes")))
    groups = [{"r": r, "notes": r["field_notes"], "words": r.get("glossary", [])} for r in cat.regions.values()]
    return render(request, "hives/field_notes.html", {"groups": groups, "crumbs": items, "ld": ld(bc)})


def tool_altitude(request):
    cat = catalogue()
    items, bc = crumbs(("Trip tools", reverse("tools")), ("Altitude planner", reverse("tool_altitude")))
    places = [{"n": p["name"], "a": int(p["altitude_m"]), "r": p["region_obj"]["name"], "s": p["region"], "u": p["url"]}
              for p in cat.places.values() if isinstance(p.get("altitude_m"), (int, float))]
    places.sort(key=lambda x: (x["r"], x["a"]))
    faqs = [
        {"q": "How fast can we gain altitude?",
         "a": "Common mountain-medicine advice is that above 3,000 m you should not raise your sleeping altitude by more than 300 to 500 m a day, and take a rest day every 3 to 4 days. Day trips higher are fine if you come back down to sleep. This planner follows that rule; it is not medical advice."},
        {"q": "What are the signs of altitude sickness?",
         "a": "Headache with any of nausea, tiredness, dizziness or poor sleep after arriving high. Mild symptoms usually settle with rest at the same height. Symptoms that get worse, breathlessness at rest or confusion mean descend at once and get medical help."},
        {"q": "Should we take medicine for altitude?",
         "a": "Only on your doctor's advice. Some doctors prescribe acetazolamide for fast ascents, such as flying into Leh. We plan rest days so you depend on medicine as little as possible."},
    ]
    return render(request, "hives/tool_altitude.html", {"crumbs": items, "places": json.dumps(places, ensure_ascii=False).replace("</", "<\\/"),
                                                        "faqs": faqs, "ld": ld(bc, faq_ld(faqs))})


def design_system(request):
    cat = catalogue()
    items, bc = crumbs(("Design system", reverse("design_system")))
    from .icons import ICONS
    return render(request, "hives/design_system.html", {"regions": list(cat.regions.values()), "icons": list(ICONS.keys()),
                                                        "tiers": [dict(v, slug=k) for k, v in TIERS.items()],
                                                        "sample": next(iter(cat.journeys.values()), None),
                                                        "crumbs": items, "ld": ld(bc)})
