# -*- coding: utf-8 -*-
"""Demo hooks: native recurring planning shifts (weekly / monthly)."""

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# Exact names — idempotent search (upgrade-safe).
WEEKLY_RECUR_SLOT_NAME = '[DEMO RECUR] Weekly cleaning — SITE-HVB-001 Harbor View — Ahmed Samir'
MONTHLY_RECUR_SLOT_NAME = '[DEMO RECUR] Monthly deep clean — SITE-PHT-003 Palm Heights — Fatima Khaled'


def ensure_recurring_planning_demo_slots(env):
    """Create one weekly and one monthly recurring planning.slot (planning.recurrency) if missing."""
    Slot = env['planning.slot'].sudo()
    company = env.company
    role = env.ref('cleaning_operations_demo_data.planning_role_cleaner', raise_if_not_found=False)
    if not role:
        _logger.warning('cleaning_operations_demo_data: planning_role_cleaner missing; skip recurring slots')
        return

    if Slot.search_count([('name', '=', WEEKLY_RECUR_SLOT_NAME)], limit=1):
        _logger.info('cleaning_operations_demo_data: weekly recurring demo slot already present')
    else:
        emp = env.ref('cleaning_operations_demo_data.hr_employee_cleaner_ahmed_samir', raise_if_not_found=False)
        res = emp.resource_id if emp else False
        if not emp or not res:
            _logger.warning('cleaning_operations_demo_data: Ahmed employee/resource missing; skip weekly recur')
        else:
            Slot.create({
                'resource_id': res.id,
                'name': WEEKLY_RECUR_SLOT_NAME,
                'role_id': role.id,
                'company_id': company.id,
                'start_datetime': '2026-05-04 06:00:00',
                'end_datetime': '2026-05-04 09:00:00',
                'repeat': True,
                'repeat_type': 'until',
                'repeat_interval': 1,
                'repeat_unit': 'week',
                'repeat_until': '2026-12-31',
            })
            _logger.info('cleaning_operations_demo_data: created weekly recurring planning shift')

    if Slot.search_count([('name', '=', MONTHLY_RECUR_SLOT_NAME)], limit=1):
        _logger.info('cleaning_operations_demo_data: monthly recurring demo slot already present')
    else:
        emp = env.ref('cleaning_operations_demo_data.hr_employee_cleaner_fatima_khaled', raise_if_not_found=False)
        res = emp.resource_id if emp else False
        if not emp or not res:
            _logger.warning('cleaning_operations_demo_data: Fatima employee/resource missing; skip monthly recur')
        else:
            Slot.create({
                'resource_id': res.id,
                'name': MONTHLY_RECUR_SLOT_NAME,
                'role_id': role.id,
                'company_id': company.id,
                'start_datetime': '2026-05-02 08:00:00',
                'end_datetime': '2026-05-02 12:00:00',
                'repeat': True,
                'repeat_type': 'until',
                'repeat_interval': 1,
                'repeat_unit': 'month',
                'repeat_until': '2026-12-31',
            })
            _logger.info('cleaning_operations_demo_data: created monthly recurring planning shift')


def post_init_hook(env):
    """Install-time: ensure recurring demo slots exist."""
    ensure_recurring_planning_demo_slots(env)


def migrate_recurring_demo_slots(cr, version):
    """Migration entry: same as hook (upgrade-time)."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    ensure_recurring_planning_demo_slots(env)
