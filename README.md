# Cleaning Operations Portal

**Odoo 19** — Field Service visits executed by **portal cleaners**, with optional GPS and photo evidence, late check-in visibility, QR entry URLs, and a printable **Portal visit summary** PDF.

This repository ships two installable addons and a **step-by-step visual guide** (screenshots below). For **print-ready** materials, use the **`doc/`** folder: an **enhanced PDF** with polished scene imagery and **placeholder callouts** where live captures or future UI will land, plus an **MVP assessment** PDF that records **gaps and the remaining backlog** (see [Documentation pack (`doc/`)](#documentation-pack-doc)). The editable slide deck remains at the repo root (`cleaning_operations_demo_presentation.pptx` / `.pdf`). Development has progressed through **four phases** — see the [version history](#version-1--initial-mvp-main) sections below.

---

## Contents

- [Features at a glance](#features-at-a-glance)
- [Modules](#modules)
- [Requirements](#requirements)
- [Installation](#installation)
- [Demo data & users](#demo-data--users)
- [Documentation pack (`doc/`)](#documentation-pack-doc)
- [Version 1 — Initial MVP (main)](#version-1--initial-mvp-main)
- [Version 2 — Delivered (Phase 2)](#version-2--delivered-phase-2)
- [Version 3 — Delivered (Phase 3)](#version-3--delivered-phase-3)
- [Version 4 — Delivered (Phase 4)](#version-4--delivered-phase-4)
- [Backlog (planned)](#backlog-planned)
- [Demo Presentation Script](#demo-presentation-script)
- [Visual walkthrough (11 scenes)](#visual-walkthrough-11-scenes)
- [Reports](#reports)
- [Presentation assets](#presentation-assets)
- [License](#license)

---

## Features at a glance

- **Manager-side:** Assign a **portal cleaner** per Field Service task; see planned window, site, late check-in, timestamps, optional GPS, duration, and before/after photos.
- **Cleaner portal:** **My Visits** list and visit detail; **Start Visit** / **End Visit**; optional geolocation at start; before/after photo uploads.
- **QR entry:** Short URL pattern `/my/fsm-visit/<task_id>` (and full path after login) for QR codes.
- **Reporting:** **Portal visit summary** (QWeb PDF) on `project.task` for internal users — requires a working **wkhtmltopdf** on the Odoo server for PDF output.

---

## Modules

| Module | Purpose |
|--------|---------|
| **`cleaning_fsm_portal_executor`** | Extends `project.task` with portal executor fields, portal routes (`/my/fsm-visits`, …), security rules, and the visit summary report. |
| **`cleaning_operations_demo_data`** | Optional demo partners, portal/internal users, HR/planning scaffolding, and many **Field Service demo tasks** covering on-time, late, WIP, and edge scenarios. |

Add the **repository root** directory (the folder that contains both module folders) to Odoo **`addons_path`**. Odoo discovers one level of addons under each path entry — you do **not** need separate path entries per subfolder.

```text
.../cleaning_operations_portal
```

Install order:

1. `cleaning_fsm_portal_executor`
2. `cleaning_operations_demo_data` (optional, recommended for demos)

---

## Requirements

- **Odoo 19** Community + **Enterprise** addons (this workflow uses **`industry_fsm`**).
- Dependencies are declared in each module’s `__manifest__.py` (`project`, `portal`, `industry_fsm`, etc.).

---

## Installation

1. Clone or copy this repository onto the Odoo server.
2. Add the **repository root** to `addons_path` in your Odoo config.
3. Update the apps list, install **`cleaning_fsm_portal_executor`**, then optionally **`cleaning_operations_demo_data`**.
4. Set passwords for demo portal users (demo data does not store passwords).

---

## Demo data & users

The **`cleaning_operations_demo_data`** module creates, among other records:

- **Sites** (as `res.partner`): e.g. Harbor View Business Center, Al Noor Medical Plaza, Palm Heights Residential Tower.
- **Users:** one internal **operations manager** and three **portal cleaners** (Ahmed, Fatima, Omar — see demo data for logins).
- **Many FSM tasks** on the standard Enterprise **Field Service** project, including assigned/unassigned visits, completed visits, in-progress visits, late check-ins, and report-friendly examples.

**Security:** no plaintext passwords in module data. After install, set passwords under **Settings → Users** or use invitation / reset flows.

For a concise data inventory, see [`cleaning_operations_demo_data/README.md`](cleaning_operations_demo_data/README.md).

---

## Documentation pack (`doc/`)

| Asset | Description |
|--------|-------------|
| **[`doc/Cleaning_Operations_Demo.pdf`](doc/Cleaning_Operations_Demo.pdf)** | **Enhanced** 11-scene demo document: high-quality screenshots, layout tuned for presentation, and **placeholder frames / callouts** marking spots reserved for additional live captures or future product UI. Use this as the primary **stakeholder PDF** when you need a polished handout beyond the Markdown walkthrough below. |
| **[`doc/Odoo_v19_Cleaning_MVP_Assessment.pdf`](doc/Odoo_v19_Cleaning_MVP_Assessment.pdf)** | **MVP assessment** — scope, what is covered in this repository, **known gaps**, and items in the [remaining backlog](#backlog-planned). (Image-based PDF; keep in sync with the backlog section here.) |
| **[`doc/guide/screenshots/`](doc/guide/screenshots/)** | **`1.png` … `11.png`** — canonical PNGs embedded in this README and aligned with the PDF scenes. |
| **[`doc/README.md`](doc/README.md)** | Short index of the `doc/` folder. |

---

## Version 1 — Initial MVP (main)

The `main` branch is the foundation. It established the complete portal execution loop for a single cleaner visit.

| Deliverable | Detail |
|-------------|--------|
| **Portal cleaner assignment** | `fsm_portal_executor_id` field on `project.task` — one portal user assigned per FSM task, separate from internal `user_ids` assignees. |
| **My Visits portal list** | Route `/my/fsm-visits` — cleaner sees only their own assigned visits with clear status indicators. |
| **Visit detail page** | Portal page per visit showing site, planned window, and evidence sections before execution. |
| **Start Visit** | Check-in timestamp recorded server-side; optional GPS latitude/longitude/accuracy captured from the browser at the moment of start. Graceful fallback when geolocation is unavailable. |
| **Before / after photo uploads** | Cleaner uploads images directly from the portal visit page; stored as `Image` fields on the task. |
| **QR entry URL** | Computed short URL `/my/fsm-visit/<task_id>` (with site hint parameters) suitable for encoding in a QR code. Backend PNG endpoint for printing. |
| **Late check-in flag** | Computed `fsm_portal_late_start` + `fsm_portal_late_start_delay_text` — compares portal check-in time against `planned_date_begin`. |
| **Portal Visit Summary report** | QWeb PDF report on `project.task` for internal users (requires wkhtmltopdf). |
| **Security** | `ir.rule` ensuring portal users can only read and act on tasks where they are the assigned portal executor. |
| **Demo data module** | Partners as sites (Harbor View, Al Noor Medical Plaza, Palm Heights), three portal cleaners, one internal manager, HR/planning scaffolding, and multiple FSM demo tasks covering on-time, late, WIP, and edge scenarios. |

---

## Version 2 — Delivered (Phase 2)

Phase 2 extended the core portal execution loop with check-out evidence, GPS on photos, and manager alerting.

| Deliverable | Detail |
|-------------|--------|
| **End Visit** | Cleaner can end the visit from the portal; check-out timestamp recorded server-side. |
| **End-of-visit GPS** | Browser geolocation captured at check-out (optional evidence, graceful fallback). |
| **GPS on photo uploads** | Latitude, longitude, and accuracy stored when the before- and after-photo are uploaded. |
| **Visit duration** | Auto-computed readable text from portal start → end timestamps. |
| **Late check-in chatter notice** | One-time chatter entry posted to the task when check-in is after the planned start — manager-facing alert. |
| **Extended demo scenarios** | Additional scenario-based demo tasks covering completed/WIP/late/wrong-cleaner cases (`fsm_portal_demo_tasks_scenarios.xml`). |

---

## Version 3 — Delivered (Phase 3)

Phase 3 upgraded sites from a `res.partner` workaround to a dedicated first-class operational model and built a site-oriented QR flow on top of it.

| Deliverable | Detail |
|-------------|--------|
| **`cleaning.site` model** | Dedicated site record with name, customer linkage, address, QR reference, readiness computation, and task count. Replaces `res.partner` as the site entity. |
| **Site QR readiness** | Computed `qr_ready` flag and `qr_readiness_note` so the manager can see at a glance if a site is ready for QR deployment. |
| **Site-based QR entry URL** | New route `/my/fsm-site/<site_id>` — cleaner scans one QR per site, then lands on the correct visit (single redirect) or a site-specific selection list (multiple valid visits). |
| **Site QR PNG endpoint** | Backend HTTP route `/cleaning_fsm_portal/site_qr_png/<site_id>` to render a downloadable PNG for printing. |
| **Site management views** | `Cleaning Sites` menu with form, list, and search views for internal managers. |
| **Demo data with `cleaning.site` records** | Three sites (Harbor View, Al Noor Medical Plaza, Palm Heights) loaded as proper `cleaning.site` rows with QR references and customer linkage. |
| **Task ↔ site constraint** | Validation that the cleaning site's customer matches the task's customer/site contact. |

---

## Version 4 — Delivered (Phase 4)

Phase 4 added manager-side operational visibility (dashboard + filters) and native Planning recurrence for scheduled visits.

| Deliverable | Detail |
|-------------|--------|
| **Manager operational dashboard** | `cleaning.fsm.manager.dashboard` model with KPI cards: total visits, not-started, in-progress, completed, late check-ins, recurring (weekly / monthly) counts. By-cleaner and by-site HTML summary tables. |
| **Dashboard views & menu** | Dedicated *Operations Dashboard* app entry; lightweight single-screen manager overview for quick drill-down. |
| **Portal-specific task filters** | Three search filters on Field Service tasks — *Portal late check-in*, *Portal visit in progress*, *Portal visit ended* — for fast manager triage without opening individual records. |
| **Native Planning recurrence** | Weekly and monthly recurring demo planning shifts created via `post_init_hook` and upgrade migration using Odoo's native `planning.recurrency` (not custom logic). |
| **Demo presentation script** | Full 19-step live-demo use-case scenario added to this README with speaking notes, screen pointers, and a quick-run order. |

---

## Backlog (planned)

The **MVP assessment PDF** (`doc/Odoo_v19_Cleaning_MVP_Assessment.pdf`) is the detailed source. Remaining roadmap items:

- **Broader stakeholder experience** — customer-facing visit visibility, SLA-style indicators, or automated notifications beyond the internal manager + portal cleaner flow.
- **Hardening for the field** — stronger **mobile** ergonomics, optional **offline** support, or push-style **reminders** for check-ins (depending on product direction).
- **Adjacent processes** — **inventory / consumables** tracking, route or multi-visit optimization, deeper wrong-site QR handling.

Refine ordering and scope from the assessment PDF and stakeholder input.

---

## Demo Presentation Script

A complete, step-by-step narrated workflow for the **Cleaning Operations Platform on Odoo 19**.  
Use this as your live demo guide — the order, speaking notes, and expected screen results are all here.

> **Speaking style reminders:**  
> Say **manager** (not admin). Say **cleaner portal flow**. Say **operational evidence**. Say **site-based QR entry**. Say **lightweight operational dashboard**. Say **practical MVP aligned with the brief**.

---

### Step 1 — Opening

> Thank you for your time.  
> In this demo, I will show a complete cleaning operations workflow built on Odoo 19.  
> I will start from the manager side, then switch to the cleaner portal flow, and finally show the operational monitoring and reporting side.

---

### Step 2 — Show the dedicated site model

**App:** Cleaning Sites → **Cleaning Sites**

Open a site record such as **Al Noor Medical Plaza**.

> I will start with the site master data.  
> Here, each cleaning site is managed as a dedicated site record, not only as a task context.  
> The site contains its name, customer linkage, address information, QR reference, QR readiness status, and a dedicated site QR entry URL.

Point to on screen:

- Name / Customer
- QR Reference / QR Ready / QR Readiness Note
- Site QR Entry URL / Open Site QR PNG
- Address / Task Count

**To create a site live:** enter Name, Customer, QR Reference (e.g. `ANMP-01`), address fields, and an optional note.

> To create a site, the manager enters the site name, customer, QR reference, and address details.  
> Once the required details are set, the site becomes QR-ready.

---

### Step 3 — Show site QR readiness

**App:** Cleaning Sites → **Cleaning Sites** (same record)

- Show **Site QR Entry URL**
- Click **Open Site QR PNG**

> Each site has its own dedicated QR entry.  
> This makes the QR flow site-oriented, so the cleaner arrives at the site, scans the site QR, and enters the correct visit workflow.

Expected: QR image opens, URL is clearly visible, site shows as QR-ready.

---

### Step 4 — Show recurring schedules

**App:** Planning → **Schedule / Planning Board**

Search for recurring demo shifts such as `[DEMO RECUR] Weekly …` and `[DEMO RECUR] Monthly …`.

> The assessment also asked for recurring schedules.  
> Here I show one weekly recurring cleaning schedule and one monthly recurring cleaning schedule.  
> Both are clearly linked in the demo naming to a site and a cleaner, so they are easy to demonstrate during review.

Point to: shift name, recurrence pattern, assigned cleaner/resource.

**To create recurrence live:** set Resource / Cleaner, Role, Start / End, Repeat, Repeat Unit (Week or Month), and Repeat Until.

> In this setup, the manager can pre-plan recurring work using native Planning recurrence, which supports operational scheduling for regular site visits.

---

### Step 5 — Show task assignment from manager side

**App:** Field Service → **Tasks**

Open a task such as **Medical waste staging room — periodic sanitize (Ahmed)**.

> Now I move to the manager-side operational task.  
> The task still lives inside Field Service, but the actual execution is handled through a portal cleaner workflow.

Point to: Task title, Customer / Site, Planned Date, Assigned Cleaner, Portal QR entry, Portal Visit Status.

**To create a task live:** fill Task Title, Project / Field Service, Customer / Site, Planned Date, Assigned Cleaner, and optional description / tags.

> The manager creates the visit task, links it to the site, sets the planned time, and assigns the portal cleaner.  
> This keeps management inside Odoo while execution is delegated through the portal.

![Scene 2 — Assignment and planned visit](doc/guide/screenshots/2.png)

---

### Step 6 — Show the manager dashboard

**App:** Operations Dashboard

> From the manager side, there is also an operational dashboard.  
> It gives a lightweight but useful overview of the visit workload, current statuses, late visits, and recurring schedule visibility.

Point to: KPI cards, counts by status, late visits, recurring weekly/monthly counts, cleaner/site summary sections.

> The dashboard is intentionally lightweight.  
> The goal is not to build a large BI platform, but to give the manager one operational screen for quick understanding and drill-down.

---

### Step 7 — Show manager list / filters

**App:** Field Service → **Tasks** → open filters

> In addition to the dashboard, the manager can quickly triage tasks using portal-specific filters.

Point to:

- **FSM: Portal late check-in**
- **FSM: Portal visit in progress**
- **FSM: Portal visit ended**

> These filters make it easy to find delayed visits, active visits, and completed visits without opening tasks one by one.

---

### Step 8 — Switch to portal cleaner

**App:** Portal → **Portal Home / My account**

Log in as a cleaner such as **Ahmed Samir**.

> Now I switch to the cleaner perspective.  
> The cleaner does not need full backend access.  
> Instead, the cleaner works through a simplified portal flow.

![Scene 3 — Portal homepage](doc/guide/screenshots/3.png)

---

### Step 9 — Show My Visits

**App:** Portal → **My Visits**

> This is the cleaner's work queue.  
> The cleaner sees only the visits assigned to them, with clear status indicators such as not started, started, ended, and late.

Point to: visit list, statuses, only assigned visits visible.

![Scene 4 — My Visits list](doc/guide/screenshots/4.png)

---

### Step 10 — Show site-QR flow

**Route:** Open the **Site QR Entry URL** from the site record, or scan the QR code.

> Here I demonstrate the site-based QR flow.  
> The cleaner scans the site QR code and is routed safely into the site-specific visit flow.

| Scenario | What to say |
|----------|-------------|
| One valid visit | *"Since this cleaner has one valid visit for this site, the system redirects directly to the correct visit."* |
| Multiple valid visits | *"If multiple valid visits exist for the same site, the system can show a site-specific selection list."* |
| No valid visit | *"If the cleaner has no valid visits for the site, the system shows a safe message without exposing unauthorized data."* |

![Scene 10 — QR / entry URL](doc/guide/screenshots/10.png)

---

### Step 11 — View visit detail before start

**App:** Portal → **My Visits → Open Visit**

> Before starting, the cleaner can see the visit details, the site information, and the evidence sections for before and after photos.

Point to: Not started status, Start Visit button, Before photo section, After photo section.

![Scene 5 — Visit detail before start](doc/guide/screenshots/5.png)

---

### Step 12 — Start Visit

**Action:** Click **Start Visit**

> When the cleaner starts the visit, the system records the check-in timestamp and attempts to capture GPS coordinates from the browser.

Expected: status changes to started, check-in time appears, GPS captured or graceful fallback message shown.

| GPS result | What to say |
|-----------|-------------|
| GPS success | *"Here, GPS was captured successfully and stored as operational evidence."* |
| GPS denied/unavailable | *"If browser geolocation is denied or unavailable, the workflow still continues safely. GPS is treated as supporting evidence, not as a blocking requirement."* |

![Scene 6 — Start visit / GPS fallback](doc/guide/screenshots/6.png)

---

### Step 13 — Upload Before photo

**Section:** Before photo — choose and upload an image.

> The cleaner now uploads the before photo to document the condition of the site before the service is completed.

Expected: upload succeeds, preview appears, GPS on upload stored if available.

---

### Step 14 — Upload After photo

**Section:** After photo — upload a second image.

> After completing the work, the cleaner uploads the after photo.  
> This creates a simple but effective visual evidence flow for the manager.

![Scene 7 — Before / after photos](doc/guide/screenshots/7.png)

---

### Step 15 — End Visit

**Action:** Click **End Visit**

> Finally, the cleaner ends the visit.  
> The system records the check-out timestamp, attempts to capture GPS at the end of the visit, and calculates the total visit duration automatically.

Expected: Ended status, check-out time, duration, end GPS if available.

![Scene 8 — Completed visit](doc/guide/screenshots/8.png)

---

### Step 16 — Return to manager task

**App:** Field Service → **Tasks** — open the same task from the backend.

> Back on the manager side, the task now shows the full operational trail:  
> the assigned cleaner, start time, end time, duration, GPS evidence, and before-and-after photos.

Point to: Assigned Cleaner, Started at, Ended at, Duration, Start GPS, End GPS, Before photo, After photo.

![Scene 1 — Manager-side operational evidence](doc/guide/screenshots/1.png)

---

### Step 17 — Show late check-in alert

**App:** Field Service → **Tasks** — open a late task.

> The solution also supports late check-in visibility.  
> If the actual start time is later than the planned start, the task is flagged as late.

Point to: Late check-in flag, Late by field, warning banner, chatter note.

> To make this more visible for the manager, the task shows a warning banner, and the event is also logged in chatter as an alert-style record.

![Scene 9 — Late check-in visibility](doc/guide/screenshots/9.png)

---

### Step 18 — Show PDF report

**App:** Field Service → **Task → Print → Portal Visit Summary**

> Finally, the manager can print a visit summary report directly from the interface.  
> This report gathers the key operational evidence into a single printable document.

Point to: visit name, site/customer, assigned cleaner, planned start, check-in / check-out, duration, late check-in flag, GPS, photos.

![Scene 11 — Visit summary report](doc/guide/screenshots/11.png)

---

### Step 19 — Closing summary

> To summarize, this solution demonstrates a complete cleaning operations workflow on Odoo 19.  
> It includes dedicated site management, site-based QR entry, recurring schedules, portal cleaner execution, check-in and check-out with timestamps and GPS, photo evidence, late-check alerts, manager operational visibility, and printable reporting.
>
> The implementation was intentionally kept practical and lightweight for demo purposes, while still covering the assessment workflow end-to-end.

---

### Quick demo order (abbreviated run)

| # | Topic |
|---|-------|
| 1 | Cleaning Sites |
| 2 | Site QR |
| 3 | Planning recurrence |
| 4 | Field Service task |
| 5 | Operations Dashboard |
| 6 | Portal My Visits |
| 7 | Site QR → Visit |
| 8 | Start Visit |
| 9 | Before photo |
| 10 | After photo |
| 11 | End Visit |
| 12 | Manager review |
| 13 | Late alert |
| 14 | PDF report |
| 15 | Closing |

---

## Visual walkthrough (11 scenes)

Screenshots live in **`doc/guide/screenshots/`** (same scenes as the PDF pack and slide deck). Use this section as a **narrated demo script** for stakeholders or QA.

### Scene 1 — Manager-side operational evidence overview

**Single-task visibility** of QR entry, late check-in, timestamps, GPS, duration, and photo evidence.

![Scene 1 — Manager-side operational evidence](doc/guide/screenshots/1.png)

---

### Scene 2 — Assignment, site, and planned visit overview

The manager sees the **visit title**, **customer / site**, **planned window**, and **assigned portal cleaner**.

![Scene 2 — Assignment and planned visit](doc/guide/screenshots/2.png)

---

### Scene 3 — Cleaner portal homepage and entry point

The cleaner reaches the workflow from a simple **portal homepage** via **My Visits**.

![Scene 3 — Portal homepage](doc/guide/screenshots/3.png)

---

### Scene 4 — Cleaner work queue / My Visits list

The cleaner sees **only assigned visits**, with clear operational status.

![Scene 4 — My Visits list](doc/guide/screenshots/4.png)

---

### Scene 5 — Visit detail before starting execution

Visit execution starts from a **portal page** with **Start Visit** and **photo evidence** sections.

![Scene 5 — Visit detail before start](doc/guide/screenshots/5.png)

---

### Scene 6 — Visit started with graceful GPS fallback

**Check-in is recorded** even when GPS cannot be captured (optional evidence).

![Scene 6 — Start visit / GPS fallback](doc/guide/screenshots/6.png)

---

### Scene 7 — Before and after photo evidence captured

The cleaner uploads **visual evidence** directly from the portal.

![Scene 7 — Before / after photos](doc/guide/screenshots/7.png)

---

### Scene 8 — Visit completed with check-out and duration

The system records **check-out** and **visit duration** between portal start and end.

![Scene 8 — Completed visit](doc/guide/screenshots/8.png)

---

### Scene 9 — Late check-in visibility for the manager

The manager can **compare planned start** vs **actual check-in** and see late indicators where applicable.

![Scene 9 — Late check-in visibility](doc/guide/screenshots/9.png)

---

### Scene 10 — QR-based entry URL for the visit

Each visit exposes a **lightweight URL** suitable for encoding in a **QR code** (assigned cleaner opens the visit after login).

![Scene 10 — QR / entry URL](doc/guide/screenshots/10.png)

---

### Scene 11 — Printable portal visit summary report

Internal users can print a **single-visit summary** (PDF when **wkhtmltopdf** is available).

![Scene 11 — Visit summary report](doc/guide/screenshots/11.png)

---

## Summary

- Manager-side visit assignment and oversight  
- Cleaner portal execution flow  
- Start and end timestamps  
- Optional GPS at check-in with graceful fallback  
- Before and after photo evidence  
- Late check-in visibility  
- QR-based visit entry  
- Printable visit summary report  

---

## Reports

- **Portal visit summary** is bound to **`project.task`** for users with project access (see module report definition).
- **PDF export** depends on **wkhtmltopdf** being installed and discoverable by the Odoo process (e.g. `bin_path` in `odoo.conf` on Windows). If PDF is unavailable, Odoo may fall back to HTML.

---

## Presentation assets

| Asset | Location |
|--------|----------|
| **Stakeholder PDF (enhanced scenes + placeholders)** | **`doc/Cleaning_Operations_Demo.pdf`** |
| **MVP assessment & remaining backlog** | **`doc/Odoo_v19_Cleaning_MVP_Assessment.pdf`** |
| PowerPoint (editable deck) | `cleaning_operations_demo_presentation.pptx` |
| PDF export of the same deck (repo root) | `cleaning_operations_demo_presentation.pdf` |
| Screenshot source (duplicate of `doc/guide/screenshots/`) | `scshots/` |
| Regeneration script | `build_demo_presentation.py` |

---

## License

Modules in this repository are **LGPL-3** unless stated otherwise in each `__manifest__.py`.

---

## Further reading

| Document | Description |
|----------|-------------|
| [`cleaning_fsm_portal_executor`](cleaning_fsm_portal_executor/) | Operational module (models, portal, report). |
| [`cleaning_operations_demo_data/README.md`](cleaning_operations_demo_data/README.md) | What demo data loads and design notes. |
| [`doc/README.md`](doc/README.md) | Index of PDFs and screenshot paths under **`doc/`**. |
