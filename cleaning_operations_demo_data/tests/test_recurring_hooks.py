# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged

from odoo.addons.cleaning_operations_demo_data.hooks import (
    MONTHLY_RECUR_SLOT_NAME,
    WEEKLY_RECUR_SLOT_NAME,
    ensure_recurring_planning_demo_slots,
)


@tagged('post_install', '-at_install', 'cleaning_demo_data')
class TestRecurringDemoHooks(TransactionCase):
    """Native planning recurrence demo slots (idempotent hook)."""

    def test_ensure_recurring_planning_demo_slots_idempotent(self):
        role = self.env.ref(
            'cleaning_operations_demo_data.planning_role_cleaner',
            raise_if_not_found=False,
        )
        if not role:
            self.skipTest('Demo planning role missing (module data not loaded)')
        emp = self.env.ref(
            'cleaning_operations_demo_data.hr_employee_cleaner_ahmed_samir',
            raise_if_not_found=False,
        )
        if not emp or not emp.resource_id:
            self.skipTest('Demo Ahmed employee/resource missing')

        ensure_recurring_planning_demo_slots(self.env)
        Slot = self.env['planning.slot'].sudo()
        w0 = Slot.search_count([('name', '=', WEEKLY_RECUR_SLOT_NAME)])
        m0 = Slot.search_count([('name', '=', MONTHLY_RECUR_SLOT_NAME)])
        self.assertGreaterEqual(w0, 1)
        self.assertGreaterEqual(m0, 1)

        ensure_recurring_planning_demo_slots(self.env)
        self.assertEqual(Slot.search_count([('name', '=', WEEKLY_RECUR_SLOT_NAME)]), w0)
        self.assertEqual(Slot.search_count([('name', '=', MONTHLY_RECUR_SLOT_NAME)]), m0)

    def test_weekly_slot_has_recurrency_when_created(self):
        """Weekly demo slot must be tied to a recurrence record."""
        if not self.env.ref(
            'cleaning_operations_demo_data.planning_role_cleaner', raise_if_not_found=False
        ):
            self.skipTest('Demo planning role missing')
        ensure_recurring_planning_demo_slots(self.env)
        slot = self.env['planning.slot'].sudo().search(
            [('name', '=', WEEKLY_RECUR_SLOT_NAME)], limit=1
        )
        self.assertTrue(slot, 'Weekly [DEMO RECUR] slot should exist after ensure_recurring_planning_demo_slots')
        self.assertTrue(slot.recurrency_id)
        self.assertEqual(slot.recurrency_id.repeat_unit, 'week')
