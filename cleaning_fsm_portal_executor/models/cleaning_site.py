# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class CleaningSite(models.Model):
    _name = 'cleaning.site'
    _description = 'Cleaning Site'
    _order = 'name'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        help='Customer/contact linked to this cleaning site.',
    )
    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state_id = fields.Many2one('res.country.state', string='State')
    zip = fields.Char(string='ZIP')
    country_id = fields.Many2one('res.country', string='Country')
    qr_reference = fields.Char(
        string='QR Reference',
        help='Short identifier printed near the QR code for this site.',
    )
    qr_ready = fields.Boolean(
        string='QR Ready',
        compute='_compute_qr_ready',
        store=True,
        help='True when the site has enough data for practical QR usage in the demo.',
    )
    qr_readiness_note = fields.Char(
        string='QR Readiness Note',
        compute='_compute_qr_ready',
    )
    note = fields.Text()
    task_ids = fields.One2many('project.task', 'fsm_cleaning_site_id', string='Visits')
    task_count = fields.Integer(compute='_compute_task_count')

    @api.depends('task_ids')
    def _compute_task_count(self):
        grouped = self.env['project.task'].read_group(
            [('fsm_cleaning_site_id', 'in', self.ids)],
            ['fsm_cleaning_site_id'],
            ['fsm_cleaning_site_id'],
        )
        counts = {
            row['fsm_cleaning_site_id'][0]: row['fsm_cleaning_site_id_count']
            for row in grouped if row.get('fsm_cleaning_site_id')
        }
        for site in self:
            site.task_count = counts.get(site.id, 0)

    @api.depends('name', 'partner_id', 'street', 'city', 'country_id', 'qr_reference')
    def _compute_qr_ready(self):
        for site in self:
            has_address = bool(site.street or site.city or site.country_id)
            has_partner = bool(site.partner_id)
            if not site.name:
                site.qr_ready = False
                site.qr_readiness_note = _('Missing site name.')
                continue
            if has_partner or has_address:
                site.qr_ready = True
                if site.qr_reference:
                    site.qr_readiness_note = _('Ready: site details and QR reference are set.')
                else:
                    site.qr_readiness_note = _('Ready: site details are set (QR reference optional).')
            else:
                site.qr_ready = False
                site.qr_readiness_note = _('Add customer or address details to make this site QR-ready.')

    @api.onchange('partner_id')
    def _onchange_partner_id_address(self):
        if not self.partner_id:
            return
        partner = self.partner_id
        if not self.street:
            self.street = partner.street
        if not self.street2:
            self.street2 = partner.street2
        if not self.city:
            self.city = partner.city
        if not self.state_id:
            self.state_id = partner.state_id
        if not self.zip:
            self.zip = partner.zip
        if not self.country_id:
            self.country_id = partner.country_id

    def action_open_site_visits(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Site Visits'),
            'res_model': 'project.task',
            'view_mode': 'list,form,kanban,calendar,pivot,graph',
            'domain': [('fsm_cleaning_site_id', '=', self.id)],
            'context': {
                'search_default_open_tasks': 1,
                'default_fsm_cleaning_site_id': self.id,
                'default_is_fsm': True,
            },
        }
