# -*- coding: utf-8 -*-
"""Backfill one-time late check-in chatter notes for existing FSM tasks (demo / upgrade)."""

def migrate(cr, version):
    from odoo import SUPERUSER_ID, api

    env = api.Environment(cr, SUPERUSER_ID, {})
    Task = env['project.task'].sudo()
    late = Task.search([
        ('fsm_portal_late_start', '=', True),
        ('fsm_portal_late_notice_posted', '=', False),
    ])
    late.filtered('is_fsm')._fsm_portal_post_late_checkin_notice()
