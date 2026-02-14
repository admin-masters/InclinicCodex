# InclinicCodex

Production-ready Django skeleton for in-clinic doctor education distribution with:

- Campaign publisher flows (campaigns, cycles, messages, assets)
- Brand manager field-rep activation/inactivation
- Field rep collateral share + reminder state logic
- Doctor verification + landing page collateral consumption
- Activity event tracking (clicks, visits, PDF/video/download)
- Dual database architecture (transaction + reporting)
- 3-hour sync command (`sync_reporting`) suitable for cron

## Project structure

- `inclinic/` - Django project settings and urls
- `core/` - Main business models/views/tests/management command
- `reporting/` - Reporting DB model
- `deployment/` - NGINX, systemd, cron samples

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --database=reporting
python manage.py runserver
```

For local SQLite testing:

```bash
export USE_SQLITE=1
```

## Cron sync

Run every 3 hours:

```bash
python manage.py sync_reporting
```

This moves `ActivityEvent` rows from transaction DB (`default`) to `ActivityEventReport` in reporting DB and deletes moved rows from transaction DB.

## Tests

```bash
python manage.py test --verbosity=2
```
