# Cleaning Operations Portal

Odoo 19 addons for a cleaning operations proof of concept. Push this repository to GitHub as a single project; both installable modules live here as siblings:

| Module | Purpose |
|--------|---------|
| **`cleaning_fsm_portal_executor`** | Field Service: assign a **portal cleaner** per visit (`fsm_portal_executor_id`), **Start Visit** from `/my/fsm-visits`. |
| **`cleaning_operations_demo_data`** | Demo partners, users, planning slots, and FSM demo tasks (depends on the module above). |

## Odoo `addons_path`

Add the **repository root** (this directory — the folder that contains both module folders) to `addons_path`, for example:

```text
.../your/checkout/cleaning_operations_portal
```

You do **not** add each submodule path separately if this directory is the root: Odoo discovers one level of addons under each path entry.

If you keep other custom addons elsewhere (e.g. `vip_hms`), list those paths too.

## Install order

1. `cleaning_fsm_portal_executor`
2. `cleaning_operations_demo_data` (optional, for demo data)

See each module’s `README.md` / manifest for details.
