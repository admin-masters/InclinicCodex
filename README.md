# InclinicCodex - Flow 01 Implementation

This repository now contains an incremental **Flow-01 (Publisher Campaign Creation & In-Clinic Setup)** implementation using Django + MySQL, with multi-database architecture retained.

## Implemented in this iteration

- Publisher authentication flow (`/login`) and **Publisher role restriction**.
- Publisher dashboard with Add/Edit campaign entry points.
- Campaign creation with:
  - auto-generated UUID (read-only identifier),
  - multi-system selection (In-Clinic implemented, others placeholders),
  - master campaign fields,
  - field-rep CSV upload + validation,
  - campaign-specific recruitment link generation.
- Campaign creation result page with selected systems and In-Clinic CTA.
- In-Clinic landing and campaign-system configuration forms.
- Campaign details page showing:
  - read-only master fields,
  - editable system-specific fields.
- Collateral management dashboard with campaign search.
- Add/Edit/Delete collateral support for:
  - PDF / Video / PDF+Video,
  - Vimeo URL validation,
  - optional webinar fields,
  - WhatsApp template with `$collateralLinks` placeholder storage.
- Doctor preview simulation page in required display order.

## Multi DB behavior

- `default` => transaction database (all writes in this flow).
- `reporting` => reserved for reporting (future flow).
- DB router is configured to keep reporting app on reporting DB.

## Deployment artifacts

- `deployment/inclinic.nginx.conf`
- `deployment/inclinic.service`
- `deployment/reporting_sync.cron`

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py migrate --database=reporting
python manage.py test --verbosity=2
```

Use SQLite for local runs/tests:

```bash
export USE_SQLITE=1
```
