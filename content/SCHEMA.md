# Himalaya Hives: content schema and house rules

Himalaya Hives (himalayahives.com) plans trips in the Himalaya and nowhere else. We think of every valley as a
hive: villages packed onto the warm side of a slope, linked by old trade paths, each with its own food, words and
festivals. Eleven hives, west to east along the arc:

kashmir · ladakh · himachal · spiti (Spiti & Lahaul) · garhwal (Garhwal, Uttarakhand) · kumaon (Kumaon, Uttarakhand) ·
nepal · darjeeling (Darjeeling & Kalimpong) · sikkim · bhutan · arunachal

Byline on everything: "Himalaya Hives Field Desk". Voice: warm, local, exact, first person plural ("we").
We are a commercial travel company with three price tiers on every trip:

- **saver**: the affordable Himalaya. Shared jeeps, state buses (HRTC, JKSRTC, UTC, SNT, NBSTC), shared Tempo
  Travellers, government tourist bungalows (JKTDC, HPTDC, GMVN, KMVN, SNT/Sikkim Tourism), well-known hostels,
  family homestays. Honest numbers. This is a big part of our audience: Indian students, young couples, families on
  a budget, solo travellers.
- **comfort**: private car with driver, good 3–4 star hotels and the best homestays.
- **signature**: the best hotels and lodges in the hive, private guide.

Audience: mostly Indian travellers (Delhi, Mumbai, Bengaluru, Kolkata) plus international visitors.

The angle that makes us different: **local-rooted facts most travel sites never tell**. Not "Gulmarg is beautiful",
but who built the trade path, what the village grows at 3,800 m, why the gompa faces that way, what the local word
for apricot is, how much the shared jeep really costs. Every such fact must be TRUE and checkable.

All content is JSON, UTF-8, under `content/<region-slug>/`. The JSON must parse (no comments, no trailing commas).
Slugs are lowercase-hyphenated ASCII and unique within their type across the WHOLE site: prefix with the region or
place if in doubt (e.g. `leh-shanti-stupa-sunset`, `kashmir-saver-srinagar-gulmarg-5n`).

## Writing rules (strict)

- Headings and titles: no full stop at the end; short, one line on desktop (≤ 60 characters).
- Plain and specific: numbers over adjectives (km, hours, metres, INR, months, °C).
- BANNED words/phrases: nestled, breathtaking, hidden gem, paradise, tapestry, embark, delve, unleash, vibrant,
  bustling, mesmerizing, stunning, magical, heaven on earth, a feast for the eyes, something for everyone,
  whether you're, look no further, ultimate guide, in this blog, in conclusion, unforgettable, world-class,
  seamless, elevate, immerse, timeless, boasts, abode of, land of gods (unless quoting the formal name
  "Devbhoomi" and explaining it), offbeat (max once per file), curated (max once per file), iconic (max once per file).
- No emoji. No exclamation marks.
- Facts that change (permits, Inner Line Permits, road and pass openings, festival dates, fees, bus fares, flight
  routes, park closures, border-area rules): state the rule as you understand it and add
  "check current status before you travel".
- Never invent reviews, awards, statistics, star ratings, founders, staff names, guide names, client counts,
  "since 19xx", or quotes from named locals. Do not invent people at all. Describe communities, not characters.
- Field notes (lesser-known facts): each must be accurate and traceable. Give a `source`: the exact English
  Wikipedia article title the fact appears in, or a named public body (e.g. "Archaeological Survey of India",
  "Botanical Survey of India", "UNESCO World Heritage Centre", "Government of Sikkim"). If you are not sure a
  fact is true, leave it out. Better 2 solid facts than 3 shaky ones (but aim for 3).
- Prices, all INR, all "indicative 2026", per person, twin sharing:
  - saver journeys: round to the nearest 500; realistic (e.g. Spiti 8 nights by bus and shared taxi with homestays
    ≈ ₹22,000–32,000 pp excluding travel to the start point).
  - comfort: round to nearest 1,000. signature: round to nearest 5,000 (e.g. Bhutan 7 nights at Amankora ≈ ₹6,00,000+).
  - `costs` rows (place pages) are real-world ranges travellers pay locally: shared taxi seat, bus fare, homestay
    night, plate of momos/thukpa, entry fee, permit fee, pony, guide day rate. Use ranges ("₹1,200–2,000").
- Stays: REAL, currently operating properties only, any price level. Government tourist bungalows/rest houses
  are welcome where they genuinely exist (JKTDC, HPTDC, GMVN, KMVN, Sikkim/Bhutan/Nepal equivalents),
  as are well-known hostel chains if they operate there (e.g. Zostel, goSTOPS, The Hosteller: only where you know
  they have a property). Do not invent amenities, room counts, awards or exact prices. If unsure it still
  operates, leave it out. Do not name individual homestays unless certain; you can describe "homestay villages".
- Distances and drive times must be realistic for mountain roads ("≈ 215 km · 8 h").
- `best_months` is ALWAYS an array of 12 integers, Jan..Dec: 2 = best, 1 = good, 0 = avoid/closed.
- `wiki` = the EXACT title of an existing English Wikipedia article about that thing (used to fetch credited
  photos from Wikimedia Commons). Use "" if none exists. Do not guess. The checker verifies these with `--wiki`.
- `image_query` = 3–6 words that would find a real photo of exactly that subject on Wikimedia Commons
  (e.g. "Key Monastery Spiti valley", "Shanti Stupa Leh").
- FAQs: real questions travellers search for (cost, permits, altitude sickness, network, ATM, best time, road
  status, safety for solo women, kids/seniors, budget); answers 40–90 words, answer first, specific.
- Altitude matters: mention acclimatisation honestly wherever sleeping altitude passes 3,000 m. No medical
  promises; say "talk to your doctor" where it fits.
- Respect: sacred sites, photography rules in monasteries, dress, plastic, leave-no-trace. Disputed areas: just
  describe travel facts; no politics.

## Files to write for each region `<r>`

### 1. `content/<r>/region.json`
```json
{
  "slug": "spiti", "name": "Spiti & Lahaul", "country": "India",
  "tagline": "≤ 8 words",
  "meta_description": "≤ 158 chars",
  "summary": "40–60 word answer-first summary",
  "intro": ["para (60–110 words)", "para", "para", "para"],
  "story": {"title": "≤ 50 chars, the hive's story",
            "chapters": [{"heading": "≤ 45 chars", "text": "90–150 words of local history, trade, belief, ecology, told as story; true facts only"}]},
                                                                                                      // exactly 4 chapters
  "facts": [["Best months", "Jun – Sep"], ["Main gateways", "…"], ["Ideal length", "…"], ["Currency", "…"],
            ["Languages", "…"], ["Permits", "…"], ["Highest road", "…"], ["Mobile network", "…"]],
  "best_months": [0,0,0,0,1,2,2,1,2,1,0,0],
  "highlights": [{"title": "…", "text": "35–60 words"}],                                             // exactly 6
  "glossary": [{"word": "Juley", "language": "Ladakhi", "meaning": "hello, goodbye, thank you"}],     // exactly 8
  "budget": [
    {"tier": "saver", "per_day_inr": "2,000–3,500", "covers": "one line: bed, food, local transport"},
    {"tier": "comfort", "per_day_inr": "…", "covers": "…"},
    {"tier": "signature", "per_day_inr": "…", "covers": "…"}],
  "money_savers": ["one specific sentence", "…"],                                                  // exactly 6
  "getting_there": "90–150 words",
  "permits": "60–120 words, or '' if none apply",
  "wiki": "Spiti Valley",
  "lat": 32.2, "lng": 78.0, "zoom": 7,
  "months": [                                                                                        // exactly 12, Jan..Dec
    {"month": "January", "rating": 0, "weather": "Kaza −20 to −5 °C, snow", "summary": "60–100 words",
     "price_level": "low | shoulder | peak", "crowd": "low | medium | high",
     "go": ["place-slug", "place-slug", "place-slug"], "events": ["festival-slug"], "tip": "one sentence"}
  ],
  "faqs": [{"q": "…", "a": "…"}]                                                                     // exactly 9
}
```

### 2. `content/<r>/places/<place-slug>.json` (10 places per region)
```json
{
  "slug": "kaza", "name": "Kaza", "region": "spiti",
  "kind": "town | village | valley | lake | pass | monastery | hill station | national park | glacier | pilgrimage town | tea country | city",
  "wiki": "Kaza, Himachal Pradesh", "image_query": "Kaza town Spiti valley",
  "lat": 32.22, "lng": 78.07, "altitude_m": 3650,
  "tagline": "≤ 70 chars",
  "meta_description": "≤ 158 chars",
  "summary": "40–60 word answer-first summary",
  "intro": ["para 70–120 words", "para", "para"],
  "facts": [["Best months", "…"], ["Nights we suggest", "2"], ["Nearest airport", "…"], ["From <hub>", "≈ 210 km · 8 h"],
            ["Altitude", "3,650 m"], ["Known for", "…"]],
  "best_months": [0,0,0,0,1,2,2,1,2,1,0,0],
  "nights": "2–3",
  "highlights": [{"title": "…", "text": "35–60 words"}],                                             // 5–6
  "field_notes": [{"fact": "25–60 words, a true lesser-known fact", "source": "exact Wikipedia title or public body"}],  // 3
  "local_word": {"word": "…", "language": "…", "meaning": "…"},
  "costs": [["Shared taxi seat, Kaza–Manali", "₹1,200–1,500"], ["Homestay with dinner and breakfast", "₹1,500–2,500 per person"]],   // 5–6 rows
  "how_to_reach": [{"mode": "Air", "text": "…"}, {"mode": "Bus", "text": "…"}, {"mode": "Road", "text": "…"}],
  "where_to_stay": "70–120 words, by budget: saver, comfort, signature where it exists",
  "stays": ["stay-slug"],                                                                            // slugs from your stays.json in this place (may be [])
  "tips": ["one sentence", "…"],                                                                     // 5
  "themes": ["road-trips", "monasteries"],                                                            // from THEMES below
  "nearby": ["place-slug"],                                                                          // 2–4 other places in this region
  "experiences": [                                                                                   // exactly 3
    {"slug": "kaza-key-monastery-morning-prayers", "title": "≤ 55 chars", "kind": "culture | spiritual | nature | wildlife | food | adventure | trek | craft | village | wellness",
     "duration": "3 hours", "best_time": "7 am, Jun–Sep", "cost": "Free entry; taxi ₹800–1,000 return",
     "image_query": "Key Monastery prayer hall", "wiki": "Key Monastery",
     "summary": "35–55 words", "body": ["para 70–120 words", "para", "para"],
     "good_for": ["couples", "families", "solo", "students", "photographers", "seniors", "first-timers"],
     "faqs": [{"q": "…", "a": "…"}]}                                                                 // exactly 3
  ],
  "faqs": [{"q": "…", "a": "…"}]                                                                     // exactly 9
}
```

### 3. `content/<r>/journeys/<journey-slug>.json` (12 per region: 4 saver, 5 comfort, 3 signature)
```json
{
  "slug": "spiti-saver-bus-and-homestay-8n", "title": "≤ 50 chars", "region": "spiti",
  "tier": "saver | comfort | signature",
  "nights": 8, "themes": ["road-trips", "homestays-and-villages"],
  "stops": [{"place": "kaza", "nights": 3}, {"place": "tabo", "nights": 1}],                           // nights sum = nights
  "start": "Shimla (ISBT Tutikandi)", "end": "Manali bus stand",
  "price_from_inr": 24500, "price_note": "one line: what the price includes and assumes",
  "transport": "one line: e.g. HRTC bus and shared taxi | Private SUV with driver",
  "group": "Private | Small group (max 12) | Shared departures",
  "best_months": [0,0,0,0,0,1,2,2,2,1,0,0],
  "pace": "Unhurried | Balanced | Active",
  "meta_description": "≤ 158 chars including 'N nights'",
  "summary": "40–60 words", "intro": ["para 70–120 words", "para"],
  "highlights": ["…"],                                                                               // 5
  "days": [{"day": 1, "title": "≤ 45 chars", "place": "kaza", "overnight": "Kaza", "drive": "≈ 210 km · 8 h or ''",
            "text": "70–130 words", "meals": "Dinner"}],                                              // days = nights + 1
  "stays": ["stay-slug"],
  "includes": ["…"], "excludes": ["…"],
  "good_to_know": ["…"],                                                                             // include acclimatisation if > 3,000 m
  "faqs": [{"q": "…", "a": "…"}]                                                                     // exactly 9
}
```
Saver journeys must actually be affordable and honest about trade-offs (shared transport, simple rooms, shared
bathrooms where true). Signature journeys use the region's best real hotels.

### 4. `content/<r>/stays.json`: array of 9 (3 budget, 3 mid, 3 luxury where the hive has them)
```json
[{"slug": "hptdc-hotel-…", "name": "…", "place": "kaza", "tier": "budget | mid | luxury",
  "kind": "government tourist bungalow | hostel | guesthouse | homestay village | boutique hotel | heritage hotel | lodge | resort | tented camp | houseboat | farmhouse | tea estate bungalow",
  "brand": "HPTDC | GMVN | Zostel | Taj | Independent | …",
  "wiki": "", "image_query": "…",
  "summary": "35–55 words", "body": ["para 70–110 words", "para"],
  "why": ["one line", "one line", "one line"], "best_for": ["…"],
  "price_band": "₹2,000–3,500 a night for a double (indicative)",
  "website": "official URL only if certain, else ''",
  "faqs": [{"q": "…", "a": "…"}]}]                                                                   // exactly 3
```

### 5. `content/<r>/guides/<guide-slug>.json` (8 per region; include one money/budget guide and one altitude or season guide)
```json
{"slug": "spiti-on-a-budget-guide", "title": "≤ 60 chars", "region": "spiti",
 "category": "planning | budget | seasons | stays | culture | food | treks | practical | wildlife | pilgrimage",
 "meta_description": "≤ 158 chars", "summary": "40–60 words answer-first",
 "sections": [{"heading": "≤ 50 chars", "paras": ["…"], "list": ["optional"], "table": {"head": ["…"], "rows": [["…"]]}}],
 "related_places": ["place-slug"],
 "faqs": [{"q": "…", "a": "…"}]}                                                                     // exactly 9
```
Guides: 1,100–1,600 words of body across 5–8 sections; use a table in at least one section.

### 6. `content/<r>/festivals.json`: array of 3
```json
[{"slug": "hemis-tsechu", "name": "Hemis Tsechu", "place": "hemis", "wiki": "Hemis Festival",
  "image_query": "Hemis festival cham dance", "when": "June–July, 10th day of the 5th Tibetan month (lunar)", "month_nums": [6, 7],
  "summary": "35–55 words", "body": ["para 70–110 words", "para", "para"], "tips": ["…", "…", "…"],
  "faqs": [{"q": "…", "a": "…"}]}]                                                                   // exactly 4
```

### 7. `content/<r>/routes.json`: array of 5 (getting between two places in this region)
```json
[{"slug": "manali-to-kaza", "from": "manali", "to": "kaza", "distance_km": 200,
  "summary": "35–55 words",
  "options": [{"mode": "Shared taxi", "time": "9–10 h", "cost": "₹1,200–1,500 a seat", "text": "50–90 words"},
              {"mode": "HRTC bus", "time": "…", "cost": "…", "text": "…"}, {"mode": "Private car", "time": "…", "cost": "…", "text": "…"}],
  "stops_on_way": ["…"], "road_status": "one line on season/opening; add check current status",
  "tip": "one sentence",
  "faqs": [{"q": "…", "a": "…"}]}]                                                                   // exactly 4
```
`from` and `to` must be place slugs you created. A gateway outside the hive (e.g. Manali for Spiti) may be one of
your 10 places only if it belongs to the hive; otherwise pick routes between your own places.

## THEMES (use these slugs only)
road-trips, treks-and-walks, monasteries, pilgrimages, wildlife-and-birds, snow-and-winter, honeymoons,
family-holidays, homestays-and-villages, food-and-tea, festivals, photography, adventure-sports, wellness-and-yoga

## Cross-references
Every slug you reference (places, stays, festivals in `events`, journey stops, nearby, related_places) must exist in
your own region's files. Run `python tools/check_region.py <r>` and then `python tools/check_region.py <r> --wiki`
until both print OK. Warnings about banned words must be fixed too.
