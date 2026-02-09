# Anti-cafe Booking Web App — Codex-ready Spec
Stack: Django (monolith + Django templates) + Bootstrap 5 + PostgreSQL

## 0) Fixed business rules (from user)
- Booking time mode: A) date + start_time + duration
- Booking target: concrete Table with chosen seats_count (<= capacity)
- Deposit:
  - deposit is configurable in admin
  - if deposit_amount == 0 => “no deposit”
  - payment processing is NOT required (deposit is informational / manual)
- Working hours + working dates are configurable in admin
- Landing:
  - separate internal Django app/module `landing`
  - static pages with links to booking system
  - root URL (`/`) routes to landing by default in `urls.py`

---

## 1) Django apps (monolith)
Create apps:
- `landing`       — static landing (TemplateViews)
- `booking`       — tables, reservations, ticket emails
- `catalog`       — board games + products (catalog only, no ordering)
- `inbox`         — contact messages from clients
- `staff`         — custom staff dashboard (Bootstrap UI)
- `site_settings` — singleton settings (SEO + contacts + deposit + schedule + telegram)

Optional:
- `integrations`  — telegram/email helper functions (can live inside apps if preferred)

---

## 2) Data models (PostgreSQL)

### 2.1 site_settings/models.py
#### SiteSettings (singleton, 1 row)
Fields:
- site_name: CharField
- site_description: TextField
- address: CharField
- phone: CharField
- logo: ImageField (optional)
- meta_title: CharField (optional)
- meta_description: CharField (optional)
- og_image: ImageField (optional)

Booking config:
- deposit_amount: DecimalField(max_digits=10, decimal_places=2, default=0)
- currency: CharField(default="EUR")
- slot_duration_choices: JSONField or hardcoded choices (default: [60,120,180,240])
- min_notice_minutes: PositiveIntegerField(default=30)

Telegram:
- tg_enabled: BooleanField(default=False)
- tg_bot_token: CharField(blank=True)
- tg_chat_id: CharField(blank=True)

Email:
- from_email: EmailField(optional)
- reply_to_email: EmailField(optional)

Meta:
- updated_at: DateTimeField(auto_now=True)

Helper behavior:
- `deposit_required = (deposit_amount > 0)`

---

### 2.2 site_settings/models.py (schedule)
We need admin-configurable working hours and working dates.

#### WeeklySchedule
- day_of_week: IntegerField(0=Mon..6=Sun), unique
- is_open: BooleanField(default=True)
- open_time: TimeField(null=True, blank=True)
- close_time: TimeField(null=True, blank=True)

Rules:
- if is_open=False => no bookings that day
- if open_time/close_time set => booking time must fit within window

#### SpecialDay
- date: DateField(unique=True)
- is_open: BooleanField(default=True)
- open_time: TimeField(null=True, blank=True)
- close_time: TimeField(null=True, blank=True)
- note: CharField(blank=True)

Rules:
- overrides WeeklySchedule for that date

---

### 2.3 booking/models.py
#### Table
- name: CharField
- capacity: PositiveIntegerField
- is_active: BooleanField(default=True)
- location_note: CharField(blank=True)

#### Reservation
- table: ForeignKey(Table)
- date: DateField
- start_time: TimeField
- duration_minutes: PositiveIntegerField (choices from SiteSettings.slot_duration_choices)
- end_time: TimeField (stored or computed; recommended: store for fast filtering)
- seats: PositiveIntegerField
- customer_name: CharField
- customer_email: EmailField
- comment: TextField(blank=True)

Status:
- status: CharField(choices=[NEW, CONFIRMED, CANCELLED, NO_SHOW, COMPLETED], default=NEW)

Ticket:
- public_code: CharField(unique=True)  # e.g. UUID4 hex or short code
- email_sent_at: DateTimeField(null=True, blank=True)

Audit:
- created_at: DateTimeField(auto_now_add=True)
- updated_at: DateTimeField(auto_now=True)

Occupies time when status in: NEW, CONFIRMED (configurable constant)

Validation rules (model clean / form clean):
- seats <= table.capacity
- table.is_active == True
- (start_time + duration) within working window for that date (WeeklySchedule/SpecialDay)
- no overlap with existing occupying reservations of same table:
  overlap if: new_start < existing_end AND new_end > existing_start

Indexing:
- index on (date, start_time)
- index on (table, date)

---

### 2.4 catalog/models.py
#### BoardGame
- title: CharField
- description: TextField(blank=True)
- players_min: PositiveIntegerField(null=True, blank=True)
- players_max: PositiveIntegerField(null=True, blank=True)
- play_time_min: PositiveIntegerField(null=True, blank=True)
- age: PositiveIntegerField(null=True, blank=True)
- image: ImageField(blank=True)
- is_available: BooleanField(default=True)

#### Product
- title: CharField
- price: DecimalField(max_digits=10, decimal_places=2)
- description: TextField(blank=True)
- image: ImageField(blank=True)
- is_available: BooleanField(default=True)

---

### 2.5 inbox/models.py
#### ContactMessage
- name: CharField
- phone: CharField
- message: TextField
- status: CharField(choices=[NEW, IN_PROGRESS, DONE], default=NEW)
- created_at: DateTimeField(auto_now_add=True)

---

## 3) Public URLs + Views (Django templates + Bootstrap)

### 3.1 Root routing (project/urls.py)
- `/` -> landing.home (default)
- `/booking/...` -> booking urls
- `/games/` `/products/` -> catalog
- `/contact/` -> inbox

### 3.2 landing app (static)
landing/urls.py:
- `/` -> TemplateView("landing/home.html")
- optional: `/about/`, `/pricing/`, `/rules/` etc.

Landing must contain links/buttons to:
- `/booking/`
- `/games/`, `/products/`
- `/contact/`

---

### 3.3 booking pages
booking/urls.py:
- `/booking/`:
  - step 1: select date
  - show available tables + available start times (based on schedule + existing reservations)
- `/booking/new/`:
  - form POST creates Reservation
  - on success: send email ticket + telegram notify (if enabled)
- `/booking/success/`:
  - “Спасибо, билет отправлен на email”
- `/booking/ticket/<public_code>/`:
  - public ticket page (read-only)

UI requirements:
- mobile-first layout (Bootstrap)
- user selects:
  - date
  - start_time
  - duration
  - table
  - seats
  - name + email
- show deposit info:
  - if deposit_amount > 0 => display “Депозит: X EUR”
  - else no deposit text

Email ticket:
- subject: “Бронирование в {site_name} на {date} {time}”
- body includes: date/time, duration, table, seats, address/phone, public_code, ticket link

---

### 3.4 catalog pages
catalog/urls.py:
- `/games/` list + details optional
- `/products/` list

No cart, no checkout.

---

### 3.5 contact page
inbox/urls.py:
- `/contact/`:
  - form: name, phone, message
  - on submit: save ContactMessage + telegram notify (if enabled)
  - success message

Anti-spam (MVP):
- honeypot field OR simple rate limit middleware

---

## 4) Staff area (custom dashboard)
Auth:
- use Django auth; staff users must have is_staff=True

staff/urls.py:
- `/staff/` -> dashboard(today)
- `/staff/reservations/` -> filter by date (today default) + status
- `/staff/tables/` -> CRUD tables
- `/staff/messages/` -> list ContactMessage
- `/staff/catalog/games/` -> CRUD BoardGame
- `/staff/catalog/products/` -> CRUD Product
- `/staff/settings/` -> edit SiteSettings + schedule models

Dashboard requirements:
- “Today reservations” list grouped by time or by table
- quick actions:
  - set status: CONFIRMED / CANCELLED
  - create manual booking
  - reassign booking (optional)
- view next days:
  - date picker -> list bookings for that date

Admin settings:
- deposit_amount
- weekly schedule per weekday
- special days overrides
- SEO fields + contacts + logo
- Telegram token + chat id + toggle + “Send test” button (POST)

Implementation note:
- Django admin can be enabled for superuser CRUD, but staff UI must exist per spec.

---

## 5) Notifications
### Email (required)
- send on successful reservation creation
- store email_sent_at when sent

### Telegram (optional, if enabled)
Trigger events:
- new reservation created
- reservation status changed by staff (cancel/confirm)
- new contact message received

Telegram message payload example:
- “Новая бронь: 2026-02-06 19:00, 2ч, Столик #3, мест: 4, Иван, email, код: ABC123”

---

## 6) Core booking logic
Implement helper services (booking/services.py):
- `get_working_window(date) -> (open_time, close_time) or None`
  - check SpecialDay first, else WeeklySchedule
- `compute_end_time(start_time, duration_minutes)`
- `is_table_available(table, date, start_time, end_time) -> bool`
- `find_available_tables(date, start_time, end_time, seats) -> list[Table]`
- `find_available_start_times(date, duration_minutes, seats)` (optional for UI)

Overlap rule:
- overlap if new_start < existing_end AND new_end > existing_start
- exclude reservations with status in [CANCELLED, NO_SHOW, COMPLETED]

---

## 7) Templates & layout
Base templates:
- `templates/base.html` (public)
- `templates/staff/base_staff.html` (staff)

Bootstrap:
- responsive navbar/footer
- forms with validation messages

SEO injection:
- in base.html: meta tags pulled from SiteSettings

---

## 8) MVP acceptance criteria
Public:
- landing at `/` loads and links to `/booking/`
- user can create reservation with date/start/duration/table/seats/name/email
- reservation prevented if:
  - outside working hours
  - on closed date
  - seats > capacity
  - overlaps existing reservation
- email ticket is sent with public ticket link
- contact form saves message + (optional) telegram notify

Staff:
- staff dashboard shows today reservations
- can view reservations for another date
- can create/edit tables
- can cancel/confirm reservations
- can manage games/products catalog
- can read contact messages
- can edit SiteSettings, weekly schedule, special days, deposit amount, telegram settings

---

## 9) Implementation order (recommended)
1) project scaffold + apps + base templates
2) SiteSettings singleton + SEO injection
3) schedule models + admin forms
4) booking models + validations + availability service
5) booking UI (date/time/duration/table/seats/name/email)
6) email ticket templates + sending
7) staff dashboard + CRUD pages
8) catalog + inbox
9) telegram integration + test button
10) polish: mobile UX, rate limit, logging
