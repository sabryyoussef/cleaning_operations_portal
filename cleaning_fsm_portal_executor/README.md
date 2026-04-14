# Cleaning FSM Portal Executor

**Odoo 19** — assign a **portal cleaner** to each **Field Service** task, execute visits from the **portal** (start/end, optional GPS, before/after photos), and print a **Portal visit summary** for internal users.

📘 **Full documentation, 11-scene screenshot guide, and demo walkthrough:** see the **[repository `README.md`](../README.md)**.

---

## What this module adds

- **Model fields** on `project.task`: portal executor, start/end timestamps, optional GPS at start, before/after images, computed QR URL, late check-in vs planned start, duration text.
- **Portal HTTP routes:** `/my/fsm-visits`, visit detail, start/end, photo uploads, QR short entry `/my/fsm-visit/<id>`.
- **Security:** `ir.rule` so portal users only see tasks where they are the assigned portal executor (plus standard project portal rules).
- **Report:** QWeb **Portal visit summary** (PDF via wkhtmltopdf when available).

---

## Dependencies

`project`, `portal`, **`industry_fsm`** (Enterprise Field Service).

---

## Install

Add the **repository root** to `addons_path`, then install this module from the Apps list.  
Optional: install **`cleaning_operations_demo_data`** for ready-made users and tasks — see [demo data README](../cleaning_operations_demo_data/README.md).

## Validation bypass (site/customer match)

By default, this module validates that `fsm_cleaning_site_id.partner_id` matches task `partner_id`.

If you need to bypass it temporarily:

- Per operation (ORM context): set context key `fsm_portal_skip_site_customer_validation=True`.
- Globally (system parameter): set `cleaning_fsm_portal_executor.skip_site_customer_validation` to `1` (truthy values: `1`, `true`, `yes`, `on`).

Use bypass only for controlled data migration or exceptional flows; keep default validation enabled for normal operations.

---

## License

LGPL-3 — see `__manifest__.py`.
