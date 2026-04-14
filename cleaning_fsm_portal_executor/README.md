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

## Manager task review paths

Managers can review a visit task from several places.

Primary flow (by task title):

1. Open **Field Service** app.
2. Go to **Tasks**.
3. In search, type the task title (for example: `Medical waste staging room - periodic sanitize (Ahmed)`).
4. Open the matching task record.
5. Review Cleaner, Cleaning Site, planned window, late check-in, photos, and portal timestamps.

Other manager paths to open tasks:

1. **Cleaning Sites -> Cleaning Sites -> open site -> Visits stat button**.
2. **Operations Dashboard -> KPI/action cards** (late, in progress, completed, etc.).
3. **Field Service -> Tasks -> Filters/Group By**:
	- Filter by portal status (Late check-in, In progress, Ended).
	- Filter tasks linked to a cleaning site.
	- Group by Cleaning Site for site-level review.

## Testing scenarios

### Scenario A: Manager finds a task by title and reviews it

1. Manager opens **Field Service -> Tasks**.
2. Manager searches by task title.
3. Manager opens task and confirms:
	- Assigned Cleaner is correct.
	- Cleaning Site is correct.
	- Customer matches site customer (unless bypass is enabled).
	- Portal fields are visible (start/end, late flag, photo evidence).

Expected result: task opens successfully and manager can review operational evidence.

### Scenario B: Site with one allowed cleaner (easy assignment)

1. Open **Cleaning Sites** and set exactly one **Allowed Cleaner**.
2. Open/create a Field Service task.
3. Select that cleaning site.

Expected result: cleaner is auto-selected on the task.

### Scenario C: Site with multiple allowed cleaners

1. Open **Cleaning Sites** and set two or more **Allowed Cleaners**.
2. Open/create a task and select the site.
3. Open the cleaner picker.

Expected result: manager can choose from the site cleaner list.

### Scenario D: Block non-allowed cleaner

1. Configure site allowed cleaners.
2. Try assigning a cleaner not in that site list.

Expected result: validation error prevents saving.

### Scenario E: Validation bypass for migration/exception flow

1. Keep a site/customer mismatch intentionally.
2. Use either context key `fsm_portal_skip_site_customer_validation=True` or system parameter `cleaning_fsm_portal_executor.skip_site_customer_validation=1`.

Expected result: mismatch validation is skipped only when bypass is enabled.

---

## License

LGPL-3 — see `__manifest__.py`.
