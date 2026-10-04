"""Line icons (24×24, stroke = currentColor). One per hive, one per experience kind and style, plus UI icons.

Drawn for Himalaya Hives; render with {% icon "ladakh" %} or {% icon "ladakh" "icon--lg" %}.
"""

ICONS = {
    # ---- hives (west to east)
    "kashmir":  # shikara on Dal with a chinar leaf above
        '<path d="M2.5 16.5c3 1.6 16 1.6 19-1.5"/><path d="M5 16.7l1-3h11l1.5 2.6"/><path d="M8 13.7V11h7v2.7"/>'
        '<path d="M7.5 11l4-2.5 4 2.5"/><path d="M2 20.5c2-.8 4-.8 6 0s4 .8 6 0 4-.8 6 0"/>'
        '<path d="M18.5 2.5l.7 2.2 1.9-1.1-.5 2.2 2.2-.2-1.6 1.5 1.5.9-2.2.5.6 1.8-1.9-1-.7 2-.7-2-1.9 1 .6-1.8-2.2-.5 1.5-.9-1.6-1.5 2.2.2-.5-2.2 1.9 1.1z"/>',
    "ladakh":  # gompa stacked on a ridge with prayer flags
        '<path d="M2 21l5-7 3 3 4-6 8 10z"/><path d="M11 9V6.5h4V9z"/><path d="M10.2 9h5.6v2.2h-5.6z"/>'
        '<path d="M13 6.5V5M12.4 5h1.2"/><path d="M2.5 6.5c2.5 1.5 5 1.5 7.5 0"/><path d="M4.5 7.4l.4 1.4 1-1M7.5 7.4l.4 1.4 1-1"/>',
    "himachal":  # kath-kuni tower temple: stone-and-timber bands, pagoda roof
        '<path d="M3 21h18"/><path d="M7.5 21V11h9v10"/><path d="M7.5 14h9M7.5 17h9"/>'
        '<path d="M5.5 11L12 6l6.5 5z"/><path d="M8 7.5L12 4l4 3.5"/><path d="M12 4V2.5"/><path d="M11 21v-2.5h2V21"/>',
    "spiti":  # mud-walled gompa on a cliff above a river bend
        '<path d="M2 21c3-1.5 5-4.5 6-9l3-2 2 3 3-1 6 9"/><path d="M8.5 9.5V6.5h5v3"/><path d="M8 6.5h6"/>'
        '<path d="M10.5 9.5V8h1v1.5"/><path d="M14.5 6.5V5h2.5v3"/><path d="M2 18.5c3 .5 5 1.5 6.5 2.5"/>',
    "garhwal":  # temple shikhara under a snow peak
        '<path d="M2 12l5-7 3 4 3-3 9 8"/><path d="M5.6 7l1.4 1 1-1"/><path d="M8.5 21v-6l3.5-4 3.5 4v6"/>'
        '<path d="M12 11V8.5"/><path d="M11.2 9.3l.8-.8.8.8"/><path d="M10.5 21v-2.5a1.5 1.5 0 0 1 3 0V21"/><path d="M3 21h18"/>',
    "kumaon":  # Aipan lotus: eight petals around a seed
        '<circle cx="12" cy="12" r="2"/><path d="M12 10c-1.2-2-1.2-4 0-6 1.2 2 1.2 4 0 6zM12 14c1.2 2 1.2 4 0 6-1.2-2-1.2-4 0-6z'
        'M10 12c-2 1.2-4 1.2-6 0 2-1.2 4-1.2 6 0zM14 12c2-1.2 4-1.2 6 0-2 1.2-4 1.2-6 0z"/>'
        '<path d="M10.6 10.6c-1.9-.5-3-1.6-3.5-3.5 1.9.5 3 1.6 3.5 3.5zM13.4 13.4c1.9.5 3 1.6 3.5 3.5-1.9-.5-3-1.6-3.5-3.5z'
        'M13.4 10.6c.5-1.9 1.6-3 3.5-3.5-.5 1.9-1.6 3-3.5 3.5zM10.6 13.4c-.5 1.9-1.6 3-3.5 3.5.5-1.9 1.6-3 3.5-3.5z"/>',
    "nepal":  # Boudhanath stupa
        '<path d="M3 21h18"/><path d="M5 21v-2h14v2"/><path d="M6.5 19a5.5 5.5 0 0 1 11 0"/>'
        '<path d="M10 10.5h4v3h-4z"/><path d="M10.9 12h.4M12.7 12h.4"/>'
        '<path d="M10.6 10.5L12 4l1.4 6.5"/><path d="M11.1 8.5h1.8M11.5 6.5h1"/><path d="M12 4V2.5"/>',
    "darjeeling":  # toy-train engine on a curve with a tea leaf
        '<path d="M3 18h12v-5H9V9H5v9"/><path d="M5 9h4"/><path d="M6 9V6.5h2V9"/><path d="M11 13v-2.5h3V13"/>'
        '<circle cx="6.5" cy="19.5" r="1.5"/><circle cx="12.5" cy="19.5" r="1.5"/><path d="M2 21.5c5 .6 12 .2 20-2"/>'
        '<path d="M18.5 12c-1.7-1.8-1.7-4.5.5-7 1.8 2.6 1.5 5.2-.5 7z"/><path d="M18.5 12c.1-2 .3-3.4.6-5"/>',
    "sikkim":  # orchid bloom
        '<path d="M12 12c-1.5-2.5-1.3-5.5.2-8 1.3 2.6 1.3 5.5-.2 8z"/><path d="M12 12c-2.8-.6-5-2.5-6-5.2 2.8.3 5 2.2 6 5.2z"/>'
        '<path d="M12 12c2.8-.6 5-2.5 6-5.2-2.8.3-5 2.2-6 5.2z"/><path d="M12 12c-2 1.3-4.5 1.6-6.5.6 1.8-1.6 4.4-1.8 6.5-.6z"/>'
        '<path d="M12 12c2 1.3 4.5 1.6 6.5.6-1.8-1.6-4.4-1.8-6.5-.6z"/><path d="M10.5 13.5c0 2 .7 3.3 1.5 4 .8-.7 1.5-2 1.5-4"/><path d="M12 17.5V22"/>',
    "bhutan":  # dzong: sloping whitewashed walls, utse tower, golden roof
        '<path d="M2 21h20"/><path d="M3.5 21l1-8h15l1 8"/><path d="M8 13l.6-4h6.8l.6 4"/>'
        '<path d="M7.5 9L12 5.5 16.5 9"/><path d="M12 5.5V3.5"/><path d="M6 16h2M16 16h2M10.5 11h3"/><path d="M10.5 21v-3h3v3"/>',
    "arunachal":  # sun rising over layered ridges
        '<path d="M7 13a5 5 0 0 1 10 0"/><path d="M12 4.5V6M5.6 7.1l1 1M18.4 7.1l-1 1M3 13h2M19 13h2"/>'
        '<path d="M2 17l4-3 3 2 4-3.5 4 3 5-2.5"/><path d="M2 21l5-3 4 2 4-2.5 7 3.5"/>',
    # ---- experience kinds
    "culture": '<path d="M3 21h18M4 9h16M12 3l9 6H3z"/><path d="M6 9v12M10 9v12M14 9v12M18 9v12"/>',
    "spiritual": '<path d="M12 3c1.5 2 1.5 3.5 0 5-1.5-1.5-1.5-3 0-5z"/><path d="M5 13c2.5 0 4.5-1 7-3 2.5 2 4.5 3 7 3"/><path d="M4 13h16l-2 4H6z"/><path d="M8 21h8"/>',
    "nature": '<path d="M2 20l7-11 4 6 3-4 6 9z"/><circle cx="17.5" cy="5.5" r="2"/>',
    "trek": '<circle cx="13" cy="4.5" r="1.6"/><path d="M9 21l2.5-6 2.5 2v4"/><path d="M11.5 15l-.5-5 3.5-2 1.5 4 3 1"/><path d="M11 10l-3 2.5"/><path d="M19 9v12"/>',
    "wildlife": '<path d="M4 15c0-4 3-7 8-7s8 3 8 7"/><path d="M7.5 9.5L6 6l3.5 2M16.5 9.5L18 6l-3.5 2"/><circle cx="9.5" cy="13" r=".8"/><circle cx="14.5" cy="13" r=".8"/><path d="M11 16.5h2l-1 1z"/><path d="M4 15c1 3 4 5 8 5s7-2 8-5"/>',
    "village": '<path d="M3 21h18"/><path d="M4 21v-7l5-4 5 4v7"/><path d="M14 21v-5l3.5-3 3.5 3v5"/><path d="M7.5 21v-3.5h3V21"/><path d="M4 14h10"/><path d="M8 7.5c0-1.2.8-1.5.8-2.8"/>',
    "food": '<path d="M3 12h18a9 9 0 0 1-18 0z"/><path d="M8 8c0-1.5 1-2 1-3.5M12 8c0-1.5 1-2 1-3.5M16 8c0-1.5 1-2 1-3.5"/>',
    "adventure": '<path d="M3 6c4-3 14-3 18 0-3 1-6 2-9 2S6 7 3 6z"/><path d="M3 6l9 9 9-9"/><path d="M12 15v2"/><path d="M10 17h4l-.5 4h-3z"/>',
    "craft": '<path d="M7 3h10M7 21h10"/><path d="M8 3c0 4 8 5 8 9s-8 5-8 9"/><path d="M16 3c0 4-8 5-8 9s8 5 8 9"/>',
    "wellness": '<path d="M12 20c-3-2.5-4.5-5.5-4.5-9 1.8.8 3.3 2.3 4.5 4.5 1.2-2.2 2.7-3.7 4.5-4.5 0 3.5-1.5 6.5-4.5 9z"/><path d="M12 15.5c-2-3-2-6 0-9 2 3 2 6 0 9z"/><path d="M4 20h16"/>',
    # ---- styles
    "road": '<path d="M8 21L11 3M16 21L13 3"/><path d="M12 7v2M12 12v2M12 17v2"/><path d="M3 21h18"/>',
    "gompa": '<path d="M3 21h18"/><path d="M5 21l1-9h12l1 9"/><path d="M8 12V8h8v4"/><path d="M7 8l5-4 5 4"/><path d="M12 4V2.5"/><path d="M10.5 21v-4h3v4"/><path d="M9 15h.01M15 15h.01"/>',
    "temple": '<path d="M3 21h18"/><path d="M6 21v-7h12v7"/><path d="M8 14l1-6h6l1 6"/><path d="M10 8l2-5 2 5"/><path d="M12 3V1.8"/><path d="M10.5 21v-3a1.5 1.5 0 0 1 3 0v3"/>',
    "snow": '<path d="M12 2v20M3.3 7l17.4 10M3.3 17L20.7 7"/><path d="M9.5 3.5L12 6l2.5-2.5M9.5 20.5L12 18l2.5 2.5"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>',
    "family": '<circle cx="7.5" cy="6" r="2"/><circle cx="16.5" cy="6" r="2"/><circle cx="12" cy="11" r="1.5"/><path d="M4.5 21v-7a3 3 0 0 1 6 0M13.5 14a3 3 0 0 1 6 0v7"/><path d="M10 21v-4a2 2 0 0 1 4 0v4"/>',
    "home": '<path d="M3 11l9-7 9 7"/><path d="M5 9.5V21h14V9.5"/><path d="M10 21v-5h4v5"/><path d="M15 6V3.5h2.5v4.3"/>',
    "festival": '<path d="M12 3c3.5 0 6 2.6 6 6.5 0 3-1.5 5-3 6.5H9c-1.5-1.5-3-3.5-3-6.5C6 5.6 8.5 3 12 3z"/><path d="M9 9.5h.01M15 9.5h.01"/><path d="M9.5 12.5c1.5 1 3.5 1 5 0"/><path d="M9 16v5M15 16v5M12 16v5"/>',
    "camera": '<rect x="3" y="7" width="18" height="13" rx="2"/><circle cx="12" cy="13.5" r="3.5"/><path d="M8.5 7l1.5-3h4l1.5 3"/>',
    # ---- UI
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "book": '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/>',
    "route": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6"/>',
    "star": '<path d="M12 3l2.6 5.6 6.1.7-4.5 4.2 1.2 6L12 16.6 6.6 19.5l1.2-6L3.3 9.3l6.1-.7z"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "sparkle": '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 16l.7 1.8 1.8.7-1.8.7-.7 1.8-.7-1.8-1.8-.7 1.8-.7z"/>',
    "altitude": '<path d="M2 20l6-9 4 5 3-3 7 7z"/><path d="M18 3v8M15.5 5.5L18 3l2.5 2.5"/>',
    "wallet": '<path d="M4 7h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a1 1 0 0 1-1-1z"/><path d="M4 7l11-3v3"/><path d="M15 13.5h5"/><circle cx="16.5" cy="13.5" r=".6"/>',
    "bus": '<rect x="4" y="3" width="16" height="15" rx="2"/><path d="M4 11h16M4 7h16"/><path d="M7 18v2.5M17 18v2.5"/><path d="M7.5 14.5h.01M16.5 14.5h.01"/>',
    "hex": '<path d="M7.5 3.5h9L21 12l-4.5 8.5h-9L3 12z"/>',
    "bed": '<path d="M3 19V6M3 15h18v4"/><path d="M21 15v-3a3 3 0 0 0-3-3h-7v6"/><circle cx="7" cy="11.5" r="2"/>',
    "leaf": '<path d="M5 19C5 10 11 5 20 4c0 9-5 15-14 15z"/><path d="M5 19c3-4 6-7 10-10"/>',
    "note": '<path d="M5 3h10l4 4v14H5z"/><path d="M15 3v4h4"/><path d="M8 11h8M8 14h8M8 17h5"/>',
    "word": '<path d="M4 5h16v10H10l-4 4v-4H4z"/><path d="M8 9.5h8M8 12h5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "tag": '<path d="M3 12V4h8l10 10-8 8z"/><circle cx="7.5" cy="8" r="1.3"/>',
    "palace": '<path d="M3 21h18"/><path d="M5 21V11h14v10"/><path d="M10 21v-3.5a2 2 0 0 1 4 0V21"/><path d="M8.5 11a3.5 3.5 0 0 1 7 0"/>',
}

ALIASES = {"water": "nature", "trekking": "trek"}


def svg(name, cls=""):
    body = ICONS.get(name) or ICONS.get(ALIASES.get(name, "")) or ICONS["sparkle"]
    return (f'<svg class="icon {cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')
