# Himalaya Hives

The website for himalayahives.com: Himalaya-only trip planning across eleven "hives" (Kashmir to Arunachal),
every trip in Saver, Comfort and Signature tiers.

It is a Django 5 site. Pages are built from JSON files in `content/`. The only database tables hold
enquiries and newsletter sign-ups.

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser        # to read enquiries at /admin/
python manage.py runserver
```

Open http://127.0.0.1:8000/. In debug mode, content edits show up when you refresh the page.

## Check the whole site

```bash
DJANGO_DEBUG=0 python tools/smoke.py               # renders every URL in the sitemap; expect "0 failures"
python tools/check_region.py <region> [--wiki]     # validates one hive's content against content/SCHEMA.md
python tools/check_journal.py                      # validates journal posts
python tools/fetch_images.py [region ...]          # refreshes credited Wikimedia Commons photos (content/images.json)
```

## Deploy

Any host that runs a Python WSGI app works (a VPS with gunicorn and nginx, Render, Railway, PythonAnywhere).

```bash
pip install -r requirements.txt gunicorn
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn hh.wsgi:application --bind 0.0.0.0:8000
```

Environment variables:

| Variable | What it does |
| --- | --- |
| `DJANGO_SECRET_KEY` | **Required in production.** A long random string |
| `DJANGO_DEBUG` | Set to `0` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated host names (default covers himalayahives.com) |
| `HH_HTTPS` | Set to `1` once the site is served over HTTPS (secure cookies, HSTS, redirect) |
| `HH_HASHED_STATIC` | Set to `1` after `collectstatic` for cache-busting file names |
| `HH_EMAIL`, `HH_PHONE`, `HH_WHATSAPP` | Public contact details shown on every page. WhatsApp is digits with country code, e.g. `919800000000` |
| `HH_NOTIFY_EMAIL` | Where new enquiries are emailed |
| `HH_SMTP_HOST`, `HH_SMTP_PORT`, `HH_SMTP_USER`, `HH_SMTP_PASSWORD`, `HH_FROM_EMAIL` | SMTP for those emails. Without them, emails print to the server log |
| `HH_GA4` | Google Analytics 4 measurement ID (optional) |

Every enquiry is also saved to the database and listed at `/admin/`.

## Before launch: business details only you can supply

These show as `[BRACKETED]` placeholders on the live site until you fill them in:

- Contact email, phone and WhatsApp are set (hello@himalayahives.com, +91 99546 34102). Override with the `HH_*` variables above.
- Office address: set `HH_ADDRESS`; it is hidden until you do.
- Policy pages (`hives/policies.py`): legal name, registered address, GSTIN, deposit percentages, cancellation scale and
  the review date. **Have a lawyer review these drafts before you take bookings.**

## Content

`content/SCHEMA.md` sets the format and house writing rules for every content file. Prices are indicative 2026
figures. Permit rules, road openings and festival dates change, so review them every season.
