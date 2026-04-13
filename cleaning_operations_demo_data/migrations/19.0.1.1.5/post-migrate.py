# -*- coding: utf-8 -*-

def migrate(cr, version):
    from odoo.addons.cleaning_operations_demo_data.hooks import migrate_recurring_demo_slots

    migrate_recurring_demo_slots(cr, version)
