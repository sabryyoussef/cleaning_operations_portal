# Cleaning Operations Demo Data

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