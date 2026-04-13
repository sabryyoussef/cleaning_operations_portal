# Cleaning Operations Demo Data

<<<<<<< HEAD
**Odoo 19** — optional **demo-only** data for the [Cleaning Operations Portal](../README.md) proof of concept.  
For the **full visual walkthrough** (11 scenes), screenshots, and presentation assets, start with the **[repository `README.md`](../README.md)**.

This module is **data-only** in terms of business logic: it does not define new models or Python workflow code; it loads XML data for partners, users, HR, planning, and Field Service tasks.

---

## Dependencies

- `base`, `portal`, `hr`, `planning`
- **`cleaning_fsm_portal_executor`** (required — provides portal executor fields and portal routes used by the demo tasks)

Enterprise: relies on **Field Service** (`industry_fsm`) through the tasks created on `industry_fsm.fsm_project`.

---

## What it loads (overview)

- **Partner taxonomy:** one category for cleaning sites.
- **Sites:** three `res.partner` records (Harbor View, Al Noor Medical Plaza, Palm Heights) with addresses and reference codes.
- **Users:** three **portal** cleaners and one **internal** manager (Nora Hassan) with appropriate groups; aligned `hr.employee` rows.
- **Planning:** cleaner role plus **multiple** `planning.slot` records (including Omar shifts) for schedule storytelling.
- **Field Service tasks:** numerous **`project.task`** records on the standard FSM project, including:
  - assigned vs unassigned portal executor;
  - planned-only, in progress, and done stages;
  - on-time, early, and late check-ins;
  - optional GPS and before/after photo placeholders on selected “report-ready” visits;
  - a labelled **[QR DEMO]** task for wrong-cleaner / QR testing.

Exact sets evolve by version — upgrade the module after pulling updates.

---

## Data design notes

- Sites are modeled as **customers** (`res.partner`) with `ref` site codes and notes for QR placeholders.
- **No passwords** are stored; set credentials after install.
- Planning slots are **illustrative** (not full recurrence engine).
- Demo tasks are tagged with readable names for **demo and QA**; keep internal consistency between assignee, times, and evidence fields.

---

## Install

1. Ensure **`addons_path`** includes the **repository root** (parent of this folder). See [main README](../README.md#installation).
2. Install **`cleaning_fsm_portal_executor`** first, then **`cleaning_operations_demo_data`**.

---

## Limitations

- Sites are not a dedicated operational model — they are partners.
- Demo data does not replace production master data or access reviews.
=======
This module preloads realistic native Odoo records for a cleaning operations proof of concept on Odoo.sh.

It is intentionally data-only:

- No custom models
- No custom business logic
- No views or menus
- No custom security files

## Dependencies

- `base`
- `portal`
- `hr`
- `planning`

## What It Loads

- One `res.partner.category` tag for cleaning sites
- Three cleaning sites as `res.partner` records
- Three cleaner portal users
- One internal manager user
- One HR department
- Two HR job positions
- Four `hr.employee` records aligned with the users
- One planning role
- Two planning slots representing weekly-like and monthly-like demo assignments

## Data Design Notes

- Sites are represented temporarily as native contacts using the partner `ref` field for site codes.
- Temporary QR placeholders are stored in the partner internal notes field.
- Cleaner users are portal users only.
- The manager is an internal user and is assigned native HR and Planning access groups for demo visibility.
- Planning slots are illustrative assignments only and do not implement true recurrence.

## Credentials

This module does not store plaintext passwords.

For Odoo.sh demo environments, the safe approach is:

1. Install the module.
2. Open the created users from Settings.
3. Set temporary passwords manually or use the standard password reset or invitation flow.

## Limitations

- Sites are not modeled as dedicated operational entities.
- Planning assignments reference employees and site names in shift titles instead of using a custom site relation.
- No portal workflow, QR flow, GPS capture, photo handling, attendance automation, alerting, or reporting is included in this module.
>>>>>>> origin/main
