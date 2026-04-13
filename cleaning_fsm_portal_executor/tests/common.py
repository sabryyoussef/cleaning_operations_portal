# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase


class CleaningFsmPortalCommon(TransactionCase):
    """Shared FSM project + partner for portal executor tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fsm_project = cls.env['project.project'].create({
            'name': 'Cleaning FSM Test Project',
            'is_fsm': True,
            'company_id': cls.env.company.id,
        })
        cls.partner = cls.env['res.partner'].create({'name': 'Test Site Co.'})
        cls.env['ir.config_parameter'].sudo().set_param('web.base.url', 'https://fsm-test.example')
