# Cleaning Operations Portal

**Odoo 19** — Field Service visits executed by **portal cleaners**, with optional GPS and photo evidence, late check-in visibility, QR entry URLs, and a printable **Portal visit summary** PDF.

This repository ships two installable addons and a **step-by-step visual guide** (screenshots below). For **print-ready** materials, use the **`doc/`** folder: an **enhanced PDF** with polished scene imagery and **placeholder callouts** where live captures or future UI will land, plus an **MVP assessment** PDF that records **gaps and the remaining backlog** (see [Documentation pack (`doc/`)](#documentation-pack-doc)). The editable slide deck remains at the repo root (`cleaning_operations_demo_presentation.pptx` / `.pdf`). This branch is **Phase 2 (Version 2)** — see the [version history](#version-1--initial-mvp-main) sections below.

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
- [Backlog (v3+)](#backlog-v3)
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
| **[`doc/Odoo_v19_Cleaning_MVP_Assessment.pdf`](doc/Odoo_v19_Cleaning_MVP_Assessment.pdf)** | **MVP assessment** — scope, what is covered in this repository, **known gaps**, and items in the [remaining backlog](#backlog-v3). (Image-based PDF; keep in sync with the backlog section here.) |
| **[`doc/guide/screenshots/`](doc/guide/screenshots/)** | **`1.png` … `11.png`** — canonical PNGs embedded in this README and aligned with the PDF scenes. |
| **[`doc/README.md`](doc/README.md)** | Short index of the `doc/` folder. |

---

## Version 1 — Initial MVP (main)

The `main` branch is the foundation. It established the core portal execution loop for a single cleaner visit.

| Deliverable | Detail |
|-------------|--------|
| **Portal cleaner assignment** | `fsm_portal_executor_id` field on `project.task` — one portal user per FSM task, separate from internal assignees. |
| **My Visits portal list** | Route `/my/fsm-visits` — cleaner sees only their own assigned visits. |
| **Visit detail page** | Portal page per visit with site info, planned window, and evidence sections. |
| **Start Visit** | Check-in timestamp recorded server-side; optional GPS captured from the browser. Graceful fallback when geolocation is unavailable. |
| **Before / after photo uploads** | Cleaner uploads images from the portal; stored as `Image` fields on the task. |
| **QR entry URL** | Computed short URL `/my/fsm-visit/<task_id>` for QR codes. Backend PNG endpoint for printing. |
| **Late check-in flag** | Computed `fsm_portal_late_start` + delay text — compares portal check-in against `planned_date_begin`. |
| **Portal Visit Summary report** | QWeb PDF report on `project.task` for internal users. |
| **Security** | `ir.rule` restricting portal users to their own tasks only. |
| **Demo data module** | Partners as sites, three portal cleaners, one internal manager, HR/planning scaffolding, and multiple FSM demo tasks. |

---

## Version 2 — Delivered (Phase 2)

This branch extends the core loop with check-out evidence, GPS on photos, and manager alerting.

| Deliverable | Detail |
|-------------|--------|
| **End Visit** | Cleaner ends the visit from the portal; check-out timestamp recorded server-side. |
| **End-of-visit GPS** | Browser geolocation captured at check-out (optional evidence, graceful fallback). |
| **GPS on photo uploads** | Latitude, longitude, and accuracy stored when before- and after-photos are uploaded. |
| **Visit duration** | Auto-computed readable text from portal start → end timestamps. |
| **Late check-in chatter notice** | One-time chatter message posted when check-in is after the planned start — manager-facing alert. |
| **Extended demo scenarios** | Scenario-based demo tasks covering completed/WIP/late/wrong-cleaner cases (`fsm_portal_demo_tasks_scenarios.xml`). |

---

## Backlog (v3+)

The **MVP assessment PDF** (`doc/Odoo_v19_Cleaning_MVP_Assessment.pdf`) is the detailed source. Planned for future phases:

- **Dedicated site model** — first-class `cleaning.site` records replacing `res.partner` as the site entity, with QR readiness, site-based QR entry route, and site management views.
- **Manager operational dashboard** — KPI cards, by-cleaner/by-site summaries, portal task filters for quick triage.
- **Native Planning recurrence** — weekly and monthly recurring demo shifts using Odoo’s planning recurrency engine.
- **Broader stakeholder experience** — customer-facing visibility, SLA-style indicators, or automated notifications.
- **Hardening for the field** — stronger mobile ergonomics, optional offline support, or push-style reminders.
- **Adjacent processes** — inventory / consumables tracking, route optimization, deeper QR wrong-site handling.

Refine ordering and scope from the assessment PDF and stakeholder input.

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
- Start **and end** timestamps
- Optional GPS at check-in **and check-out** with graceful fallback
- **GPS captured on photo uploads**
- Before and after photo evidence
- **Auto-computed visit duration**
- Late check-in visibility with **chatter alert**
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
