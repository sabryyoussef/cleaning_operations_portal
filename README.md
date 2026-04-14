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

## Manager review quick paths

Recommended day-to-day review flow (by task title):

1. Open **Field Service -> Tasks**.
2. Search by task title.
3. Open task and review Cleaner, Cleaning Site, portal start/end, late flag, and photos.

Other useful manager entry points:

1. **Cleaning Sites -> open site -> Visits** stat button.
2. **Operations Dashboard** KPI/action cards (late, in progress, completed, etc.).
3. **Field Service -> Tasks** filters and group by (portal status, cleaning site).

For detailed assignment/review test scenarios, see [cleaning_fsm_portal_executor/README.md](cleaning_fsm_portal_executor/README.md).

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

Phase 3 introduced dedicated cleaning sites and manager-side operational visibility while keeping the portal execution flow from earlier phases.

| Deliverable | Detail |
|-------------|--------|
| **`cleaning.site` model** | Dedicated site record with customer linkage, address fields, QR reference, readiness computation, note, and visit count. Replaces `res.partner` as the site entity. |
| **Task ↔ site linkage** | `fsm_cleaning_site_id` on `project.task`, auto-fills the customer when possible and validates site/customer consistency. |
| **Site management UI** | `Cleaning Sites` menu with list and form views for internal managers, including visit drill-down from the site record. |
| **Site QR readiness** | Computed `qr_ready` flag and `qr_readiness_note` so the manager can see whether a site is ready for QR deployment. |
| **Manager operational dashboard** | Lightweight **Operations Dashboard** app entry with KPI cards for total, not started, in progress, completed, and late visits. |
| **Manager summaries** | Dashboard sections aggregate visits by cleaner and by site for quick operational review. |
| **Portal-specific task filters** | Search filters for portal late check-in, in-progress visits, ended visits, and tasks linked to a cleaning site. |
| **Group by cleaning site** | Search view support for grouping Field Service tasks by dedicated cleaning site. |
| **Dedicated site demo data** | Three `cleaning.site` records loaded for Harbor View, Al Noor Medical Plaza, and Palm Heights. |

---

## Version 4 — Delivered (Phase 4)

Phase 4 added site-based QR entry, recurring planning support, and the final demo-facing presentation layer.

| Deliverable | Detail |
|-------------|--------|
| **Site-based QR entry URL** | `cleaning.site` now computes a dedicated site QR URL so a cleaner can scan once at the site and land in the correct visit flow. |
| **Site QR landing flow** | New routes `/my/fsm-site/<site_id>` and `/my/fsm-sites/<site_id>` support redirect-to-single-visit, multi-visit selection, and safe no-visit handling. |
| **Site QR PNG endpoint** | Backend HTTP route `/cleaning_fsm_portal/site_qr_png/<site_id>` renders a printable QR image for each site. |
| **Site QR actions in backend** | Site form exposes the QR entry URL and an action to open the QR PNG directly from the manager UI. |
| **Native Planning recurrence** | Weekly and monthly recurring demo planning shifts created via `post_init_hook` and upgrade migration using Odoo's native `planning.recurrency` (not custom logic). |
| **Recurring dashboard metrics** | Dashboard now shows weekly and monthly recurring schedule counts with drill-down actions into matching planning slots. |
| **Demo presentation script** | Full 19-step live-demo use-case scenario added to this README with speaking notes, screen pointers, and a quick-run order. |

---

## Backlog (planned)

The **MVP assessment PDF** (`doc/Odoo_v19_Cleaning_MVP_Assessment.pdf`) is the detailed source. Remaining roadmap items:

- **Broader stakeholder experience** — customer-facing visit visibility, SLA-style indicators, or automated notifications beyond the internal manager + portal cleaner flow.
- **Hardening for the field** — stronger **mobile** ergonomics, optional **offline** support, or push-style **reminders** for check-ins (depending on product direction).
- **Adjacent processes** — **inventory / consumables** tracking, route or multi-visit optimization, deeper wrong-site QR handling.

Refine ordering and scope from the assessment PDF and stakeholder input.

---

## Demo Guide

This section is a practical runbook for product review, QA, and live walkthroughs.

### Step 1 — Scope and sequence

Review in this order: manager setup, planning, task assignment, portal execution, manager verification, and report output.

### Step 2 — Review site master data

**App:** Cleaning Sites -> Cleaning Sites

Open a site such as **Al Noor Medical Plaza** and verify:

- Name and Customer
- QR Reference, QR Ready, QR Readiness Note
- Site QR Entry URL and Open Site QR PNG action
- Address fields and Visits count

For live setup, fill Name, Customer, QR Reference, address fields, and optional notes.

### Step 3 — Verify site QR readiness

From the same site record:

1. Check Site QR Entry URL.
2. Click Open Site QR PNG.

Expected result: QR image opens and site is QR-ready.

### Step 4 — Verify recurring schedules

**App:** Planning -> Schedule / Planning Board

Search for recurring demo shifts such as `[DEMO RECUR] Weekly ...` and `[DEMO RECUR] Monthly ...`.

Review recurrence pattern, linked cleaner/resource, and date window.

### Step 5 — Review task assignment from manager side

**App:** Field Service -> Tasks

Open a task such as **Medical waste staging room - periodic sanitize (Ahmed)**.

Verify task title, customer/site, planned date, assigned cleaner, QR entry, and portal visit status fields.

![Scene 2 — Assignment and planned visit](doc/guide/screenshots/2.png)

### Step 6 — Review manager dashboard

**App:** Operations Dashboard

Review KPI cards, status counts, late visits, recurring weekly/monthly counts, and cleaner/site summaries.

### Step 7 — Review manager task filters

**App:** Field Service -> Tasks

Apply portal filters and verify results:

- FSM: Portal late check-in
- FSM: Portal visit in progress
- FSM: Portal visit ended

### Step 8 — Open cleaner portal

Log in as a portal cleaner (example: **Ahmed Samir**) and open portal home.

![Scene 3 — Portal homepage](doc/guide/screenshots/3.png)

### Step 9 — Review My Visits queue

**App:** Portal -> My Visits

Verify only assigned visits are visible and status labels are correct.

![Scene 4 — My Visits list](doc/guide/screenshots/4.png)

### Step 10 — Validate site QR entry behavior

Open the site QR entry URL or scan the site QR code.

Validate all outcomes:

- One valid visit: redirect directly to the visit.
- Multiple valid visits: show site-specific selection.
- No valid visit: show safe, non-disclosing message.

![Scene 10 — QR / entry URL](doc/guide/screenshots/10.png)

### Step 11 — Review visit detail before start

**App:** Portal -> My Visits -> Open Visit

Verify not-started status, Start Visit button, and before/after photo sections.

![Scene 5 — Visit detail before start](doc/guide/screenshots/5.png)

### Step 12 — Start visit and verify check-in

Click Start Visit.

Expected result: status becomes started, check-in time is recorded, and GPS is captured when available (or safely skipped).

![Scene 6 — Start visit / GPS fallback](doc/guide/screenshots/6.png)

### Step 13 — Upload before photo

Upload a before photo and verify preview and saved evidence.

### Step 14 — Upload after photo

Upload an after photo and verify preview and saved evidence.

![Scene 7 — Before / after photos](doc/guide/screenshots/7.png)

### Step 15 — End visit and verify completion

Click End Visit.

Expected result: ended status, checkout timestamp, duration, and end GPS when available.

![Scene 8 — Completed visit](doc/guide/screenshots/8.png)

### Step 16 — Review completed task from manager side

Return to **Field Service -> Tasks** and open the same task.

Verify assigned cleaner, start/end timestamps, duration, GPS, and before/after photos.

![Scene 1 — Manager-side operational evidence](doc/guide/screenshots/1.png)

### Step 17 — Review late check-in visibility

Open a late task and verify late flag, delay text, warning banner, and chatter note.

![Scene 9 — Late check-in visibility](doc/guide/screenshots/9.png)

### Step 18 — Print visit summary report

**App:** Field Service -> Task -> Print -> Portal Visit Summary

Verify printed output includes visit, site/customer, cleaner, planned start, start/end, duration, late flag, GPS, and photos.

![Scene 11 — Visit summary report](doc/guide/screenshots/11.png)

### Step 19 — Close review

Confirm the end-to-end flow: site setup, QR entry, recurrence, portal execution, manager monitoring, and report output.

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
